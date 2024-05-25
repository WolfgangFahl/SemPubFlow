"""
Created on 2023-06-19

@author: wf
"""
from fastapi.responses import RedirectResponse
from ngwidgets.input_webserver import InputWebserver, InputWebSolution
from ngwidgets.login import Login
from ngwidgets.users import Users
from ngwidgets.webserver import WebserverConfig
from nicegui import Client, app, ui

from sempubflow.admin import Admin
from sempubflow.elements.proceedings_form import ProceedingsForm
from sempubflow.homepage_selector import HomePageSelector
from sempubflow.orcid_auth import ORCIDAuth
from sempubflow.scholar_selector import ScholarSelector
from sempubflow.version import Version



class SemPubFlowWebServer(InputWebserver):
    """
    webserver
    """

    @classmethod
    def get_config(cls) -> WebserverConfig:
        copy_right = "(c)2023-2024 Wolfgang Fahl"
        config = WebserverConfig(
            copy_right=copy_right, 
            version=Version(), 
            default_port=9857,
            short_name="spf"
        )
        server_config = WebserverConfig.get(config)
        server_config.solution_class = SemPubFlowSolution
        return server_config

    def __init__(self):
        """
        constructor
        """
        InputWebserver.__init__(self, config=SemPubFlowWebServer.get_config())
        users = Users("~/.sempubflow/")
        self.login = Login(self, users)
        self.orcid_auth = ORCIDAuth()
        pass

        @ui.page("/")
        async def home(client: Client):
            if not self.login.authenticated():
                return RedirectResponse("/login")

            return await self.page(client, SemPubFlowSolution.home)


        @ui.page("/admin")
        async def admin(client: Client):
            if not self.login.authenticated():
                return RedirectResponse("/login")
            return await self.page(client, SemPubFlowSolution.admin)

        @ui.page("/settings")
        async def settings(client: Client):
            if not self.login.authenticated():
                return RedirectResponse("/login")
            return await self.page(client, SemPubFlowSolution.settings)

        @ui.page("/user/{username}")
        async def show_user(client: Client, username: str):
            if not self.login.authenticated():
                return RedirectResponse("/login")
            return await self.page(client, SemPubFlowSolution.show_user,username)

        @ui.page("/scholar")
        async def scholar_search(client: Client):
            return await self.page(client, SemPubFlowSolution.scholar_search)

        @ui.page("/create_volume")
        async def create_volume(client: Client):
            return await self.page(client, SemPubFlowSolution.create_volume)

        @ui.page("/login")
        async def login(client: Client) -> None:
            return await self.page(client, SemPubFlowSolution.show_login)

class SemPubFlowSolution(InputWebSolution):
    """
    the Solution for the Semantic Publishing Workflow

    """
    def __init__(self, webserver: SemPubFlowWebServer, client: Client):
        """
        Initialize the solution

        Calls the constructor of the base solution
        Args:
            webserver (SemPubFlowWebServer): The webserver instance associated with this context.
            client (Client): The client instance this context is associated with.
        """
        super().__init__(webserver, client)  # Call to the superclass constructor
        self.login=webserver.login
        
    def configure_menu(self):
        """
        configure the menu
        """
        self.link_button("scholar", "/scholar", "school")
        self.link_button("volume", "/create_volume", "library_books")
        self.link_button("admin", "/admin", "database")
        username = app.storage.user.get("username", "?")
        self.link_button(username, f"/user/{username}", "person")

   
    async def show_user(self, username: str):
        """
        show the user with the given username
        """

        def show():
            ui.label(username)

        await self.setup_content_div(show)

    async def admin(self):
        """
        admin interface
        """

        def show():
            self.admin_view = Admin(self)

        await self.setup_content_div(show)

    async def settings(self):
        def show():
            ui.label("timeout")
            self.timeout_slider = ui.slider(min=0.5, max=10).props("label-always")
            # .bind_value(self,"timeout")

        await self.setup_content_div(show)
        
    async def logout(self):
        await self.login.logout()
        
    async def show_login(self):
        await self.login.login(self)

    async def create_volume(self):
        def show():
            self.volume_form = ProceedingsForm()

        await self.setup_content_div(show)

    async def scholar_search(self):
        def show():
            self.scholar_selector = ScholarSelector(self)

        await self.setup_content_div(show)

    async def home(self):
        """
        home page selection
        """

        def show():
            self.homepageSelector = HomePageSelector(self)

        await self.setup_content_div(show)
