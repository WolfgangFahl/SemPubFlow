import traceback
import re
from typing import Callable, List, Optional, Union

from nicegui import ui
from nicegui.element import Element

from sempubflow.models.affiliation import Affiliation
from sempubflow.models.scholar import Scholar
from ngwidgets.dict_edit import DictEdit

class AffiliationForm(DictEdit):
    """
    Affiliation of a scholar typically describes an institution or organization
    """

    def __init__(self, affiliation: Optional[Affiliation] = None, **kwargs):
        self.affiliation = affiliation or Affiliation()
        
        # Customization for affiliation fields
        affiliation_customization = {
            '_form_': {"icon": "house"},
            'name': {'label': 'Name', 'size': 50},
            'location': {'label': 'Location', 'size': 50},
            'country': {'label': 'Country', 'size': 50},
            'wikidata_id': {'label': 'Wikidata ID', 'size': 50, 'validation': Validator.validate_wikidata_qid},
        }
        super().__init__(self.affiliation, customization=affiliation_customization,**kwargs)
     

class ScholarForm(DictEdit):
    """
    Form to enter data about a scholar
    """

    def __init__(self, scholar:Optional[Scholar]=None, add_affiliation_callback: Optional[Callable] = None, **kwargs):
        self.scholar = scholar or Scholar()
        try:     
            scholar_customization = {
                '_form_': {"icon": "person"},
                'given_name': {'label': 'Given Name', 'size': 50},
                'family_name': {'label': 'Family Name', 'size': 50},
                'wikidata_id': {'label': 'Wikidata ID', 'size': 50, 'validation': Validator.validate_wikidata_qid},
                # add other field customizations as needed
                'orcid_id': {'label': 'ORCID ID', 'size': 50},
                'dblp_author_id': {'label': 'DBLP Author ID', 'size': 50},
                'official_website': {'label': 'Official Website', 'size': 50},
            }
            super().__init__(self.scholar, customization=scholar_customization,**kwargs)
            self.affiliations_container = ui.card()
            ui.button(icon='add', text="Add Affiliation", on_click=lambda: add_affiliation_callback(self))    
        except Exception as ex:
            print(ex)
            print(traceback.format_exc())
            pass
 
    def add_affiliation_form(self, affiliation: Optional[Affiliation] = None):
        with self.affiliations_container:
            ui.notify(f"Adding Affiliation")
            af = AffiliationForm(affiliation)
            if self.scholar.affiliation is None:
                    self.scholar.affiliation = []
            self.scholar.affiliation.append(af.affiliation)
            ui.separator()

class ScholarsListForm(Element):
    """
    Handles a list of scholar forms
    """
    ADD_BUTTON_NOTIFICATION = "Adding Scholar"
    ADD_BUTTON_LABEL = "Add Scholar"
    EXPANSION_LABEL_PREFIX = "Scholar: "

    def __init__(self):
        super().__init__(tag="div")
        self.scholars = []
        self.scholars_container = ui.card()
        ui.button(icon='add', text=self.ADD_BUTTON_LABEL, on_click=lambda: self.add_scholar_form())

    def add_scholar_form(self):
        with self.scholars_container:
            ui.notify(self.ADD_BUTTON_NOTIFICATION)
            with ui.row().classes("w-full") as row:
                form = ScholarForm(add_affiliation_callback=self.affiliation_dialog)
                self.scholars.append(form.scholar)
                with form.card:
                    ui.button(icon="delete", on_click=lambda: self.delete_scholar(form, row))

    def delete_scholar(self, scholar_form: ScholarForm, element: Element):
        """
        delete the selected scholar
        Returns:

        """
        self.scholars.remove(scholar_form.scholar)
        self.scholars_container.remove(element)

    def affiliation_dialog(self, scholar: ScholarForm):
        with ui.dialog() as dialog, ui.card():
            ui.label('Choose Affiliation')
            ui.button("New", on_click=lambda: self.add_new_affiliation(dialog, scholar))
            for affiliation in self.affiliations:
                ui.button(affiliation.name, on_click=lambda: self.set_affiliation(dialog, affiliation, scholar))
            ui.button('Close', on_click=dialog.close)
        dialog.open()

    @staticmethod
    def set_affiliation(dialog: ui.dialog, affiliation: Affiliation, scholar: ScholarForm):
        scholar.add_affiliation_form(affiliation)
        ui.notify(f"Added affiliation {affiliation.name} to scholar {scholar.scholar.name}")
        dialog.close()

    @staticmethod
    def add_new_affiliation(dialog: ui.dialog, scholar: ScholarForm):
        dialog.close()
        scholar.add_affiliation_form()
    @property
    def affiliations(self) -> List[Affiliation]:
        """
        affiliations of the scholars
        Returns:
            List of affiliations
        """
        affiliations = dict()
        for scholar in self.scholars:
            if scholar.affiliation:
                for affiliation in scholar.affiliation:
                    if affiliation.name not in affiliations:
                        affiliations[affiliation.name] = affiliation
        return list(affiliations.values())


class Validator:
    """
    Validators for input fields
    """

    @classmethod
    def validate_wikidata_qid(cls, value: Union[str, None]) -> bool:
        """
        Checks if the given value is a valid wikidata Qid
        Args:
            value: value to check

        Returns:
            bool: True if the value is a valid Qid or the value is None. Otherwise False
        """
        valid = False
        if value is None:
            valid = True
        elif re.match(r"Q\d+", value):
            valid = True
        return valid
