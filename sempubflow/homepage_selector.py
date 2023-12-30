"""
Created on 2023-12-30

@author: wf
"""
from nicegui import ui
from ngwidgets.dict_edit import DictEdit
from sempubflow.llm import LLM
from sempubflow.event_info import EventInfo
from sempubflow.homepage import Homepage

class HomePageSelector:
    """
    select a home page and analyze it
    """

    def __init__(self,webserver):
        """
        constructor
        """
        self.valid = False
        self.timeout = 3.0
        self.webserver=webserver

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
        homepage = Homepage(volume=0, url=url)
        self.valid = homepage.check_url(timeout=self.timeout)
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