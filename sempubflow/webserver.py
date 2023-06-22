"""
Created on 2023-06-19

@author: wf
"""
from nicegui import ui
from sempubflow.homepage import Homepage
from sempubflow.llm import LLM
from sempubflow.event_info import EventInfo

class HomePageSelector:
    """
    select a home page and analyze it
    """
    def __init__(self):
        """
        constructor
        """
        self.valid=False
        self.homepage_input=ui.input(
            label="homepage",
            placeholder="""url of the event's homepage""",
            on_change=self.on_url_change,
            validation={"URL invalid": lambda _url:self.valid },   
        )
        self.homepage_input.props("size=80")
        self.status = ui.label()
        self.event_details=ui.textarea().props("cols=80")
        self.llm=LLM()
        self.event_info=EventInfo(self.llm)
        
    def on_url_change(self,event):
        """
        react on changing the url homepage value
        """
        url=event.sender.value
        self.valid=Homepage.check_url(url)
        if self.valid:
            event_details=self.event_info.get_meta_data(url)
            status_msg=self.event_info.status_msg()
            self.event_details.set_value(event_details)
        else:
            status_msg="❌"
        self.status.set_text(status_msg)
        pass
    
class WebServer:
    """
    webserver
    """

    def __init__(self):
        """
        constructor
        """
        pass

    def run(self, host, port):
        """
        run the ui
        """
        ui.link('Semantic Publishing Flow on GitHub', 'https://github.com/WolfgangFahl/SemPubFlow')
        self.homepageSelector=HomePageSelector()
        ui.run(title="Semantic Publishing Flow", host=host, port=port, reload=False)
