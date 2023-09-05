from typing import Any, Callable

from nicegui import ui
from nicegui.element import Element

from sempubflow.models.scholar import Scholar


class ScholarSuggestion(Element):
    """
    display a Scholar
    """

    def __init__(self, scholar: Scholar, on_select: Callable[[Scholar], Any]):
        super().__init__(tag="div")
        self.scholar = scholar
        self._on_select_callback =  on_select
        with ui.card().tight() as card:
            card.on("click", self.on_select)
            with ui.card_section() as section:
                section.props(add="horizontal")
                with ui.card_section():
                    with ui.avatar():
                        if scholar.image:
                            ui.image(source=scholar.image)
                ui.separator().props(add="vertical")
                with ui.card_section():
                    with ui.row():
                        self.scholar_label = ui.label(self.scholar.label)
                    with ui.row():
                        self.scholar_name = ui.label(f"{self.scholar.given_name} {self.scholar.family_name}")
                    with ui.row():
                        self._show_identifier()

    def on_select(self):
        """
        Handle selection of the suggestion card
        """
        return self._on_select_callback(self.scholar)

    def _show_identifier(self):
        """
        display all identifier of the scholar
        """
        if self.scholar.wikidata_id:
            with ui.element('div'):
                ui.avatar(
                        icon="img:https://www.wikidata.org/static/favicon/wikidata.ico",
                        color=None,
                        size="sm",
                        square=True
                )
                ui.link(text=self.scholar.wikidata_id,
                        target=f"https://www.wikidata.org/wiki/{self.scholar.wikidata_id}", new_tab=True)
        if self.scholar.dblp_author_id:
            with ui.element('div'):
                ui.element('i').classes('ai ai-dblp')
                ui.link(text=self.scholar.dblp_author_id,
                        target=f"https://dblp.org/pid/{self.scholar.dblp_author_id}", new_tab=True)
        if self.scholar.orcid_id:
            with ui.element('div'):
                ui.element('i').classes('ai ai-orcid')
                ui.link(text=self.scholar.orcid_id,
                        target=f"https://orcid.org/{self.scholar.orcid_id}", new_tab=True)
