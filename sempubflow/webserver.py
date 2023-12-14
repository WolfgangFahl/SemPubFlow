"""
Created on 2023-06-19

@author: wf
"""
from typing import List, Optional

from fastapi.responses import RedirectResponse
from ngwidgets.dict_edit import DictEdit
from ngwidgets.input_webserver import InputWebserver
from ngwidgets.login import Login
from ngwidgets.users import Users
from ngwidgets.webserver import WebserverConfig
from nicegui import Client, app, run, ui

from sempubflow.elements.proceedings_form import ProceedingsForm
from sempubflow.elements.suggestion import ScholarSuggestion
from sempubflow.event_info import EventInfo
from sempubflow.homepage import Homepage
from sempubflow.llm import LLM
from sempubflow.models.scholar import Scholar, ScholarSearchMask
from sempubflow.orcid_auth import ORCIDAuth
from sempubflow.services.dblp import Dblp
from sempubflow.services.wikidata import Wikidata
from sempubflow.version import Version


class HomePageSelector:
    """
    select a home page and analyze it
    """

    def __init__(self):
        """
        constructor
        """
        self.valid = False
        self.timeout = 3.0

        self.homepage_input = ui.input(
            label="homepage",
            placeholder="""url of the event's homepage""",
            on_change=self.on_url_change,
            validation={"URL invalid": lambda _url: self.valid},
        )
        with ui.element("div").classes("w-full h-full"):
            with ui.splitter() as splitter:
                with splitter.before:
                    self.homepage_input.props("size=80")
                    self.status = ui.label()
                    self.llm = LLM()
                    self.event_info = EventInfo(self.llm)
                    self.event_details = ui.card().tight()
                with splitter.after:
                    self.homepage_frame = ui.html("").classes("w-full h-screen")

    def on_url_change(self, event):
        """
        react on changing the url homepage value
        """
        url = event.sender.value
        self.valid = Homepage.check_url(url, timeout=self.timeout)
        if self.valid:
            self.homepage_frame.content = f"""<iframe width="100%" height="100%" src="{url}"></iframe>
"""
            event_dict = self.event_info.get_meta_data(url)
            status_msg = self.event_info.status_msg()
            with self.event_details:
                self.dict_edit = DictEdit(event_dict)
        else:
            status_msg = "❌"
            self.event_details.clear()
        self.status.set_text(status_msg)
        pass


class ScholarSelector:
    """
    Select a scholar with auto-suggestion
    """

    def __init__(self):
        ui.add_head_html(
            '<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/jpswalsh/academicons@1/css/academicons.min.css">'
        )
        self.selected_scholar: Optional[Scholar] = None
        self.suggestion_list_wd: Optional[ui.element] = None
        self.suggestion_list_dblp: Optional[ui.element] = None
        self.scholar_selection()

    @ui.refreshable
    def scholar_selection(self):
        """
        Display input fields for scholar data with autosuggestion
        """
        scholar = self.selected_scholar if self.selected_scholar else Scholar()
        with ui.element("div").classes("w-full"):
            with ui.splitter().classes("h-full  w-full") as splitter:
                with splitter.before:
                    with ui.row():
                        self.given_name_input = ui.input(
                            label="given_name",
                            placeholder="""given name""",
                            on_change=self.suggest_scholars,
                            value=scholar.given_name,
                        )
                        self.family_name_input = ui.input(
                            label="family_name",
                            placeholder="""family name""",
                            on_change=self.suggest_scholars,
                            value=scholar.family_name,
                        )
                    with ui.row():
                        self.identifier_type_input = ui.select(
                            options={
                                "wikidata_id": "Wikidata",
                                "dblp_author_id": "dblp",
                                "orcid_id": "ORCID",
                            },
                            value="wikidata_id",
                            on_change=self.suggest_scholars,
                        )
                        self.identifier_input = ui.input(
                            label="identifier",
                            placeholder="""identifier-""",
                            on_change=self.suggest_scholars,
                            value=scholar.wikidata_id,
                        )
                with splitter.after:
                    with ui.element("div").classes("columns-2 w-full h-full gap-2"):
                        ui.label("wikidata")
                        self.suggestion_list_wd = ui.column().classes(
                            "rounded-md border-2 p-3"
                        )

                        ui.label("dblp")
                        self.suggestion_list_dblp = ui.column().classes(
                            "rounded-md border-2"
                        )

    async def suggest_scholars(self):
        """
        based on given input suggest potential scholars

        Returns:
            List of scholars
        """
        search_mask = self._get_search_mask()
        if (
            len(search_mask.name) > 4
        ):  # quick fix to avoid queries on empty input fields
            suggested_scholars_dblp = await run.io_bound(
                Dblp().get_scholar_suggestions, search_mask
            )
            self.update_suggestion_list(
                self.suggestion_list_dblp, suggested_scholars_dblp
            )
            suggested_scholars_wd = await run.io_bound(
                Wikidata().get_scholar_suggestions, search_mask
            )
            self.update_suggestion_list(self.suggestion_list_wd, suggested_scholars_wd)

    def update_suggestion_list(self, container: ui.element, suggestions: List[Scholar]):
        container.clear()
        with container:
            if len(suggestions) <= 10:
                with ui.scroll_area():
                    for scholar in suggestions:
                        ScholarSuggestion(
                            scholar=scholar, on_select=self.select_scholar_suggestion
                        )
            else:
                ui.spinner(size="lg")
                ui.label(
                    f"{'>' if len(suggestions) == 10000 else ''}{len(suggestions)} matches..."
                )
        return []

    def select_scholar_suggestion(self, scholar: Scholar):
        """
        Select the give Scholar by updating the input fields to the selected scholar and storing teh object internally
        Args:
            scholar: scholar that should be selected
        """
        self.selected_scholar = scholar
        self.scholar_selection.refresh()
        if self.suggestion_list_wd:
            self.suggestion_list_wd.clear()
        if self.suggestion_list_dblp:
            self.suggestion_list_dblp.clear()

    def _get_search_mask(self) -> ScholarSearchMask:
        """
        Get the current search mask from the input fields
        Returns:
            ScholarSearchMask: current search input
        """
        ids = dict()
        if self.identifier_type_input.value:
            ids[self.identifier_type_input.value] = self.identifier_input.value
        search_mask = ScholarSearchMask(
            label=None,
            given_name=self.given_name_input.value,
            family_name=self.family_name_input.value,
            **ids,
        )
        return search_mask


class WebServer(InputWebserver):
    """
    webserver
    """

    @classmethod
    def get_config(cls) -> WebserverConfig:
        copy_right = "(c)2023 Wolfgang Fahl"
        config = WebserverConfig(
            copy_right=copy_right, version=Version(), default_port=9857
        )
        return config

    def __init__(self):
        """
        constructor
        """
        InputWebserver.__init__(self, config=WebServer.get_config())
        users = Users("~/.sempubflow/")
        self.login = Login(self, users)
        self.orcid_auth = ORCIDAuth()
        pass

        @ui.page("/")
        async def home(client: Client):
            if not self.login.authenticated():
                return RedirectResponse("/login")
            return await self.home()

        @ui.page("/settings")
        async def settings(client: Client):
            if not self.login.authenticated():
                return RedirectResponse("/login")
            return await self.settings()

        @ui.page("/scholar")
        async def scholar_search(client: Client):
            return await self.scholar_search()

        @ui.page("/create_volume")
        async def create_volume(client: Client):
            return await self.create_volume()

        @ui.page("/login")
        async def login(client: Client) -> None:
            return await self.login.login(client)

    def configure_menu(self):
        self.link_button("scholar", "/scholar", "scholar")
        self.link_button("volume", "/create_volume", "library_books")
        username = app.storage.user.get("username", "?")
        ui.label(username)

    async def settings(self):
        def show():
            ui.label("timeout")
            self.timeout_slider = ui.slider(min=0.5, max=10).props("label-always")
            # .bind_value(self,"timeout")

        await self.setup_content_div(show)

    async def create_volume(self):
        def show():
            self.volume_form = ProceedingsForm()

        await self.setup_content_div(show)

    async def scholar_search(self):
        def show():
            self.scholar_selector = ScholarSelector()

        await self.setup_content_div(show)

    async def home(self):
        def show():
            self.homepageSelector = HomePageSelector()

        await self.setup_content_div(show)

    def configure_run(self):
        self.args.storage_secret = self.orcid_auth.client_secret
        pass
