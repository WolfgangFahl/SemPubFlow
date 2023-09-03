from nicegui import events, ui
from nicegui.element import Element


class DragAndDrop(Element):
    """
    display a Drag and Drop field
    """

    def __init__(self):
        super().__init__(tag="div")

        ui.upload(
                on_upload=self.handle_upload,
                on_rejected=lambda: ui.notify('Rejected!'),
                max_file_size=1_000_000
        ).props('accept=.pdf').classes('max-w-full')


    def handle_upload(self, e: events.UploadEventArguments):
        ui.notify(f'Uploaded {e.name}')
        text = e.content.read().decode('utf-8')

