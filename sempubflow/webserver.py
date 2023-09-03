"""
Created on 2023-06-19

@author: wf
"""
from typing import List, Optional
from fastapi.responses import RedirectResponse
from nicegui import app,ui, Client

from sempubflow.elements.suggestion import ScholarSuggestion
from sempubflow.homepage import Homepage
from sempubflow.llm import LLM
from sempubflow.event_info import EventInfo
from sempubflow.dict_edit import DictEdit
from sempubflow.models.scholar import Scholar, ScholarSearchMask
from sempubflow.services.dblp import Dblp
from sempubflow.services.wikidata import Wikidata
from sempubflow.version import Version
from sempubflow.users import Users
from sempubflow.orcid_auth import ORCIDAuth

class HomePageSelector:
    """
    select a home page and analyze it
    """
    def __init__(self):
        """
        constructor
        """
        self.valid=False
        self.timeout=3.0
        
        self.homepage_input=ui.input(
            label="homepage",
            placeholder="""url of the event's homepage""",
            on_change=self.on_url_change,
            validation={"URL invalid": lambda _url:self.valid },   
        )
        self.homepage_input.props("size=80")
        self.status = ui.label()
        self.llm=LLM()
        self.event_info=EventInfo(self.llm)
        self.event_details=ui.card().tight()
        
    def on_url_change(self,event):
        """
        react on changing the url homepage value
        """
        url=event.sender.value
        self.valid=Homepage.check_url(url,timeout=self.timeout)
        if self.valid:
            event_dict=self.event_info.get_meta_data(url)
            status_msg=self.event_info.status_msg()
            self.dict_edit=DictEdit(self.event_details,event_dict)
        else:
            status_msg="❌"
            self.event_details.clear()
        self.status.set_text(status_msg)
        pass


class ScholarSelector:
    """
    Select a scholar with auto-suggestion
    """

    def __init__(self):
        ui.add_head_html('<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/jpswalsh/academicons@1/css/academicons.min.css">')
        self.selected_scholar: Optional[Scholar] = None
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
                                value=scholar.given_name
                        )
                        self.family_name_input = ui.input(
                                label="family_name",
                                placeholder="""family name""",
                                on_change=self.suggest_scholars,
                                value=scholar.family_name
                        )
                    with ui.row():
                        self.identifier_type_input = ui.select(
                                options={"wikidata_id": "Wikidata", "dblp_author_id": "dblp", "orcid_id": "ORCID"},
                                value="wikidata_id",
                                on_change=self.suggest_scholars,
                        )
                        self.identifier_input = ui.input(
                                label="identifier",
                                placeholder="""identifier-""",
                                on_change=self.suggest_scholars,
                                value=scholar.wikidata_id
                        )
                with splitter.after:
                    with ui.element('div').classes('columns-2 w-full h-full gap-2'):
                        ui.label("wikidata")
                        self.suggestion_list_wd = ui.column().classes("rounded-md border-2 p-3")

                        ui.label("dblp")
                        self.suggestion_list_dblp = ui.column().classes("rounded-md border-2")

    def suggest_scholars(self):
        """
        based on given input suggest potential scholars

        Returns:
            List of scholars
        """
        search_mask = self._get_search_mask()
        suggested_scholars_dblp = Dblp().get_scholar_suggestions(search_mask)
        self.update_suggestion_list(self.suggestion_list_dblp, suggested_scholars_dblp)
        suggested_scholars_wd = Wikidata().get_scholar_suggestions(search_mask)
        self.update_suggestion_list(self.suggestion_list_wd, suggested_scholars_wd)

    def update_suggestion_list(self, container: ui.column, suggestions: List[Scholar]):
        container.clear()
        with container:
            if len(suggestions) <= 10:
                with ui.scroll_area():
                    for scholar in suggestions:
                        ScholarSuggestion(scholar=scholar, on_select=self.select_scholar_suggestion)
            else:
                ui.spinner(size='lg')
                ui.label(f"{'>' if len(suggestions) == 10000 else ''}{len(suggestions)} matches...")
        return []

    def select_scholar_suggestion(self, scholar: Scholar):
        """
        Select the give Scholar by updating the input fields to the selected scholar and storing teh object internally
        Args:
            scholar: scholar that should be selected
        """
        self.selected_scholar = scholar
        self.scholar_selection.refresh()
        self.suggestion_list.clear()

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
                **ids
        )
        return search_mask

 
class WebServer:
    """
    webserver
    """

    def __init__(self):
        """
        constructor
        """
        self.users=Users()
        self.orcid_auth=ORCIDAuth()
        pass
       
        @ui.page('/')
        async def home(client: Client):
            if not self.authenticated():
                return RedirectResponse('/login')
            return await self.home(client)
        
        @ui.page('/settings')
        async def settings(client:Client):
            return await self.settings(client)
        
        @ui.page('/scholar')
        async def scholar_search(client:Client):
            return await self.scholar_search(client)
        
        @ui.page('/login')
        async def login(client:Client) -> None:    
            return await self.login(client)
        
    def link_button(self, name: str, target: str, icon_name: str,new_tab:bool=True):
        """
        Creates a button with a specified icon that opens a target URL upon being clicked.
    
        Args:
            name (str): The name to be displayed on the button.
            target (str): The target URL that should be opened when the button is clicked.
            icon_name (str): The name of the icon to be displayed on the button.
            new_tab(bool): if True open link in new tab
    
        Returns:
            The button object.
        """

        btn_classes = "q-btn q-btn-item non-selectable no-outline q-btn--standard q-btn--rectangle bg-primary text-white q-btn--actionable q-focusable q-hoverable"
        with ui.link(text="", target=target, new_tab=True).classes(btn_classes) as link:
            link.style(add="text-decoration:none")
            with ui.row():
                ui.icon(icon_name)
                ui.label(name)
    
    def tool_button(self,tooltip:str,icon:str,handler:callable=None,toggle_icon:str=None)->ui.button:
        """
        Creates an  button with icon that triggers a specified function upon being clicked.
    
        Args:
            tooltip (str): The tooltip to be displayed.
            icon (str): The name of the icon to be displayed on the button.
            handler (function): The function to be called when the button is clicked.
            toggle_icon (str): The name of an alternative icon to be displayed when the button is clicked.
    
        Returns:
            ui.button: The icon button object.
            
        valid icons may be found at:    
            https://fonts.google.com/icons
        """
        icon_button=ui.button("",icon=icon, color='primary').tooltip(tooltip).on("click",handler=handler)  
        icon_button.toggle_icon=toggle_icon
        return icon_button   
    
    def setup_menu(self):
        """Adds a link to the project's GitHub page in the web server's menu."""
        with ui.header() as self.header:
            self.link_button("home","/","home")
            self.link_button("scholar","/scholar","scholar")
            self.link_button("github",Version.cm_url,"bug_report")
            self.link_button("chat",Version.chat_url,"chat")
            self.link_button("help",Version.doc_url,"help")

    async def settings(self,client:Client):
        self.setup_menu()
        ui.label("timeout")
        timeout_slider = ui.slider(min=0.5, max=10).props('label-always')
        #.bind_value(self,"timeout")

    async def scholar_search(self,client:Client):
        self.setup_menu()
        scholar_selector = ScholarSelector()
        pass

    async def home(self,client:Client):
        self.setup_menu()
        homepageSelector=HomePageSelector()
        pass
    
    def authenticated(self)->bool:
        result=app.storage.user.get('authenticated', False)
        return result
    
    async def login(self,client:Client):
        def try_login() -> None:  # local function to avoid passing username and password as arguments
            if self.users.check_password(username.value, password.value):
                app.storage.user.update({'username': username.value, 'authenticated': True})
                ui.open('/')
            else:
                ui.notify('Wrong username or password', color='negative')

        if self.authenticated():
            return RedirectResponse('/')
        with ui.card().classes('absolute-center'):
            username = ui.input('Username').on('keydown.enter', try_login)
            password = ui.input('Password', password=True, password_toggle_button=True).on('keydown.enter', try_login)
            ui.button('Log in', on_click=try_login)
  
    def run(self, args):
        """
        run the ui with the given command line arguments
        """
        self.args=args
        ui.run(title=Version.name, host=args.host, port=args.port, show=args.client,reload=False,storage_secret=self.orcid_auth.client_secret)
    