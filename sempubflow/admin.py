"""
Created 2023-12-24


"""
from nicegui import ui
class Admin:
    """
    administration
    """
    
    def __init__(self,webserver):
        self.webserver=webserver
        self.setup()
        
    def setup(self):
        ui.label("Admin")