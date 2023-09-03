"""
Created on 2023-06-19

@author: wf
"""
from typing import List, Optional

from nicegui import ui

from sempubflow.elements.suggestion import ScholarSuggestion
from sempubflow.homepage import Homepage
from sempubflow.llm import LLM
from sempubflow.event_info import EventInfo
from sempubflow.dict_edit import DictEdit
from sempubflow.models.scholar import Scholar, ScholarSearchMask
from sempubflow.services.wikidata import Wikidata


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
        with ui.splitter() as splitter:
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
                self.suggestion_list = ui.column()

    def suggest_scholars(self) -> List[Scholar]:
        """
        based on given input suggest potential scholars

        Returns:
            List of scholars
        """
        search_mask = self._get_search_mask()
        self.suggestion_list.clear()
        suggested_scholars = Wikidata().get_scholar_suggestions(search_mask)
        # suggested_scholars = Dblp().get_scholar_suggestions(search_mask)
        #ToDo: merge suggestion results
        with self.suggestion_list:
            if len(suggested_scholars) <= 10:
                for scholar in suggested_scholars:
                    ScholarSuggestion(scholar=scholar, on_select=self.select_scholar_suggestion)
            else:
                ui.spinner(size='lg')
                ui.label(f"{'>' if len(suggested_scholars) == 10000 else ''}{len(suggested_scholars)} matches...")
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
        pass
    
    @staticmethod
    def menu():
        ui.link('Semantic Publishing Flow on GitHub', 'https://github.com/WolfgangFahl/SemPubFlow')
        # https://nicegui.io/documentation/menu
        #with ui.row().classes('w-full items-center'):
        #    result = ui.label().classes('mr-auto')
        #    with ui.button(icon='menu'):
        #        with ui.menu() as menu:
        #            ui.menu_item('Menu item 1', lambda: result.set_text('Selected item 1'))
        #            ui.menu_item('Menu item 2', lambda: result.set_text('Selected item 2'))
        #            ui.menu_item('Menu item 3 (keep open)',
        #                         lambda: result.set_text('Selected item 3'), auto_close=False)
        #            ui.separator()
        #            ui.menu_item('Close', on_click=menu.close)
       
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

    @ui.page('/scholar')
    @staticmethod
    def scholar():
        WebServer.menu()
        scholar_selector = ScholarSelector()
  
    def run(self, host, port):
        """
        run the ui
        """
        ui.run(title="Semantic Publishing Flow", host=host, port=port, reload=False)
