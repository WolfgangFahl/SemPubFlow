import re
from typing import Callable, List, Optional, Union

from nicegui import ui
from nicegui.binding import bind_from
from nicegui.element import Element

from sempubflow.models.affiliation import Affiliation
from sempubflow.models.scholar import Scholar


class AffiliationForm(Element):
    """
    Affiliation of a scholar typically describes an institution or organization
    """

    def __init__(self, affiliation: Optional[Affiliation] = None):
        super().__init__(tag="div")
        if affiliation is None:
            affiliation = Affiliation()
        self.affiliation = affiliation
        ui.input(label="name").bind_value(self.affiliation, "name")
        ui.input(label="location").bind_value(self.affiliation, "location")
        ui.input(label="country").bind_value(self.affiliation, "country")
        ui.input(
                label="wikidata_id",
                validation={"Invalid Wikidata ID": lambda value: Validator.validate_wikidata_qid(value)}
         ).bind_value(self.affiliation, "wikidata_id")


class ScholarForm(Element):
    """
    Form to enter data about a scholar
    """

    def __init__(self, add_affiliation_callback: Optional[Callable] = None):
        super().__init__(tag="div")
        self.scholar = Scholar()
        ui.input(label="given name").bind_value(self.scholar, "given_name")
        ui.input(label="family name").bind_value(self.scholar, "family_name")
        ui.input(
                label="wikidata id",
                validation={"Invalid Wikidata ID": Validator.validate_wikidata_qid}
        ).bind_value(self.scholar, "wikidata_id")
        ui.input(label="ORCID id").bind_value(self.scholar, "orcid_id")
        ui.input(label="dblp author id").bind_value(self.scholar, "dblp_author_id")
        ui.input(label="official website").bind_value(self.scholar,"official_website")
        self.affiliations_container = ui.card()
        if add_affiliation_callback is None:
            add_affiliation_callback = ScholarForm.add_affiliation_form
        ui.button(icon='add', text="Add Affiliation", on_click=lambda: add_affiliation_callback(self))

    def add_affiliation_form(self, affiliation: Optional[Affiliation] = None):
        with self.affiliations_container:
            ui.notify(f"Adding Affiliation")
            with ui.expansion(text="Affiliation", icon='house').classes('w-full') as expansion:
                af = AffiliationForm(affiliation)
                bind_from(expansion._props, 'label', af.affiliation, "name",
                          backward=lambda x: f"Affiliation: {x}")
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
                with ui.expansion(text="Scholar", icon='person') as expansion:
                    form = ScholarForm(add_affiliation_callback=self.affiliation_dialog)
                    bind_from(expansion._props, 'label', form.scholar, "name", lambda x: f"{self.EXPANSION_LABEL_PREFIX}{x}")
                    self.scholars.append(form.scholar)
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
