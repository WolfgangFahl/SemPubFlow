"""
Created on 2023-06-19

@author: wf
"""
from nicegui import ui
import urllib.request


class WebServer:
    """
    webserver
    """

    def __init__(self):
        """
        constructor
        """
        pass

    def check_url(self, url:str)->bool:
        """
        
        check the given url
        
        Args:
            url(str): the url to check
            
        Returns:
            bool: True if the url is reachable
        """
        try:
            code = urllib.request.urlopen(url).getcode()
        except Exception as _ex:
            return False
        return code == 200

    def run(self, host, port):
        """
        run the ui
        """
        ui.link('Semantic Publishing Flow on GitHub', 'https://github.com/WolfgangFahl/SemPubFlow')
        ui.input(
            label="homepage",
            placeholder="""url of the event's homepage""",
            on_change=lambda e: result.set_text("you typed: " + e.value),
            validation={"URL invalid": lambda url: self.check_url(url)},
        )
        result = ui.label()

        ui.run(title="Semantic Publishing Flow", host=host, port=port, reload=False)
