"""
Created on 2023-06-19

@author: wf
"""
from nicegui import Client,ui
from sempubflow.homepage import Homepage
from sempubflow.llm import LLM
from sempubflow.event_info import EventInfo
from sempubflow.dict_edit import DictEdit

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
 
class WebServer:
    """
    webserver
    """

    def __init__(self):
        """
        constructor
        """
        pass
    
    @staticmethod
    def menu():
        ui.link('Semantic Publishing Flow on GitHub', 'https://github.com/WolfgangFahl/SemPubFlow')
   
    @ui.page('/')
    @staticmethod
    def home():
        WebServer.menu()
        homepageSelector=HomePageSelector()
    
    @ui.page('/settings')
    @staticmethod
    def settings():
        WebServer.menu()
        ui.label("timeout")
        timeout_slider = ui.slider(min=0.5, max=10).props('label-always')
        #.bind_value(self,"timeout")
  
    def run(self, host, port):
        """
        run the ui
        """
        ui.run(title="Semantic Publishing Flow", host=host, port=port, reload=False)
