import datetime
import json
from typing import Optional
from urllib.parse import urlparse

import dateutil.parser
from nicegui import ui
from nicegui.binding import bind_from, bind_to
from nicegui.element import Element
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers.data import JsonLexer

from sempubflow.elements.scholar_form import ScholarForm, ScholarsListForm
from sempubflow.elements.suggestion import ScholarSuggestion
from sempubflow.models.proceedings import Conference, CustomDict, Event, EventType, Proceedings, Workshop
from dataclasses import asdict

from sempubflow.models.templates.ceurws import CeurVolumePage


class ProceedingsForm(Element):
    """
    Form to enter all data needed for a proceedings
    """

    def __init__(self):
        super().__init__(tag="div")
        self.proceeding = Proceedings()
        with ui.stepper().props('vertical').classes('w-full') as stepper:
            with ui.step('Proceedings'):
                ui.label('Proceedings title')
                ui.input(label="title").bind_value(self.proceeding, "title")
                with ui.input('publication_date') as date:
                    date.bind_value(self.proceeding, "publication_date",
                            forward=lambda value: dateutil.parser.parse(value) if value else None,
                            backward=lambda value: value.isoformat() if isinstance(value, datetime.datetime) else value)
                    with date.add_slot('append'):
                        ui.icon('edit_calendar').on('click', lambda: menu.open()).classes('cursor-pointer')
                    with ui.menu() as menu:
                        ui.date().bind_value(date)
                with ui.stepper_navigation():
                    ui.button('Next', on_click=stepper.next)
            with ui.step('Event'):
                ui.label("Please enter information about the event")
                event_forms = ui.card()
                with ui.button(icon='add', text="Add Event"):
                    with ui.menu() as menu:
                        ui.menu_item('Workshop', lambda: self.add_event_form(Workshop, event_forms))
                        ui.menu_item('Conference', lambda: self.add_event_form(Conference, event_forms))
                with ui.stepper_navigation():
                    ui.button('Next', on_click=stepper.next)
                    ui.button('Back', on_click=stepper.previous).props('flat')
            with ui.step('Editors'):
                ui.label('Please enter the editors of the proceedings')
                sf = ScholarsListForm()
                self.proceeding.editor = sf.scholars
                with ui.stepper_navigation():
                    ui.button('Done', on_click=lambda: ui.notify('Yay!', type='positive'))
                    ui.button('Back', on_click=stepper.previous).props('flat')
        ui.label().bind_text_from(self, "proceeding", backward=lambda x: str(x))
        DisplayResults(self.proceeding)

    def add_event_form(self, clazz: type, container: ui.card):
         with container:
            ui.notify(f"Add {clazz.__name__}")
            with ui.expansion(text=clazz.__name__, icon='event') as expansion:
                expansion.classes('w-full')
                ef = EventForm(clazz)
                bind_from(expansion._props, 'label', ef.event, "title", backward=lambda x: f"{clazz.__name__}: {x}")
                if self.proceeding.event is None:
                    self.proceeding.event = []
                self.proceeding.event.append(ef.event)

            ui.separator()


class EventForm(Element):
    """
    Form for an event
    """

    def __init__(self, clazz: type):
        super().__init__(tag="div")
        if clazz is None:
            clazz = Event
        self.event = clazz()
        with ui.card().classes('w-full'):
            with ui.splitter().classes('w-full') as splitter:
                with splitter.before:
                    ui.input(label="title").bind_value(self.event, "title")
                    ui.input(
                            label="acronym",
                            validation={'Input too long': lambda value: len(value) < 35 if value else True}
                    ).bind_value(self.event, "acronym")
                    ui.input(label="location").bind_value(self.event, "location")
                    ui.input(label="country").bind_value(self.event, "country")
                    ui.input(
                            label="official website",
                            validation={'Invalid URL': lambda value: self.validate_url(value)}
                             ).bind_value(self.event, "official_website")
                    ui.select(
                            EventType.get_record(),
                            value=self.event.type.name
                    ).bind_value(self.event, 'type',
                                 forward=lambda value: EventType[value],
                                 backward=lambda value: value.name
                                 )
                with splitter.after:
                    ui.date().props('range').bind_value(self.event, "date_range")

    def validate_url(self, url: str):
        if url is None:
            valid = True
        else:
            try:
                result = urlparse(url)
                valid = all([result.scheme, result.netloc])
            except:
                valid = False
        return valid


class DisplayResults(Element):
    """
    Display results in different formats
    """

    def __init__(self, proceedings: Proceedings):
        super().__init__(tag="div")
        self.proceedings = proceedings
        with ui.tabs().classes('w-full') as tabs:
            one = ui.tab('JSON')
            two = ui.tab('CEUR-WS')
        with ui.tab_panels(tabs, value=two).classes('w-full'):
            with ui.tab_panel(one):
                html = ui.html().bind_content_from(self, "proceedings", backward=lambda value: self.convert_to_json_html(value))
            with ui.tab_panel(two):
                ui.html().bind_content_from(self, "proceedings", backward=lambda value: CeurVolumePage(value).render())

    @classmethod
    def convert_to_json_html(cls, proceedings: Proceedings) -> Optional[str]:
        """
        convert given proceeding to json encoded in html
        Args:
            proceedings:

        Returns:
            str: html
        """
        if proceedings is None:
            return None
        record = asdict(proceedings, dict_factory=CustomDict)
        content = highlight(
                code=json.dumps(record, indent=4),
                lexer=JsonLexer(),
                formatter=HtmlFormatter(style="colorful", full=True)
        )

        return content


if __name__ in {"__main__", "__mp_main__"}:
    pf = ProceedingsForm()
    ui.run(port=14000)
