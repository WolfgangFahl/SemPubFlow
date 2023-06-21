"""
Created on 2023-06-19

@author: wf
"""
from nicegui import ui
from sempubflow.homepage import Homepage

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
            validation={"URL invalid": lambda url:self.valid },   
        )
        self.homepage_input.props("size=80")
        self.status = ui.label()
        
    def on_url_change(self,event):
        """
        """
        url=event.sender.value
        self.valid=Homepage.check_url(url)
        if self.valid:
            homepage=Homepage(url)
            text=homepage.get_text()
            chars=len(text)
            lines=text.count('\n')
            status_msg=f"✅ {lines} lines and {chars} chars"
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
