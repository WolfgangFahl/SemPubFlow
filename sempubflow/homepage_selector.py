"""
Created on 2023-12-30

@author: wf
"""
from ngwidgets.dict_edit import DictEdit
from ngwidgets.llm import LLM
from nicegui import run, ui

from sempubflow.event_info import EventInfo
from sempubflow.homepage import Homepage


class HomePageSelector:
    """
    select a home page and analyze it
    """

    def __init__(self, webserver, model="gpt-3.5-turbo-16k"):
        """
        constructor
        """
        self.valid = False
        self.timeout = 3.0
        self.webserver = webserver
        self.model = model
        self.llm = LLM(model=model)
        self.event_info = EventInfo(self.llm, debug=self.webserver.debug)
        self.setup()

    def setup(self):
        """
        setup my ui components
        """
        self.homepage_input = ui.input(
            label="homepage",
            placeholder="""url of the event's homepage""",
            on_change=self.on_url_change,
            validation={"URL invalid": lambda _url: self.valid},
        )

        with ui.element("div").classes("w-full h-full"):
            with ui.splitter() as splitter:
                with splitter.before as self.event_view:
                    self.homepage_input.props("size=80")
                    self.status = ui.label()
                    self.event_details = ui.card().tight()
                with splitter.after:
                    self.homepage_frame = ui.html("").classes("w-full h-screen")

    def get_event_from_hompage(self):
        """
        get the event from my homepage
        """
        try:
            # potentially make model and temperature chooseable
            event = self.event_info.get_event_metadata_from_homepage(
                self.homepage, model=self.model, temperature=0.0
            )
            with self.event_details:
                self.dict_edit = DictEdit(event)
                self.dict_edit.expansion.open()
        except Exception as ex:
            self.webserver.handle_exception(ex)

    async def on_url_change(self, args):
        """
        react on changing the url homepage value
        """
        try:
            url = args.sender.value
            self.homepage = Homepage(volume=0, url=url)
            self.valid = self.homepage.check_url(timeout=self.timeout)
            if self.valid:
                self.homepage_frame.content = f"""<iframe width="100%" height="100%" src="{url}"></iframe>
    """
                ui.notify("analyzing homepage content")
                await run.io_bound(self.get_event_from_hompage)
                status_msg = self.event_info.status_msg()
                self.status.set_text(status_msg)
            else:
                status_msg = "❌"
                self.event_details.clear()
                self.status.set_text(status_msg)
        except Exception as ex:
            self.webserver.handle_exception(ex)
