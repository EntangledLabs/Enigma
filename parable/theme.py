from contextlib import contextmanager

from nicegui import ui
from .menu import menu

@contextmanager
def frame(navigation_title: str):
    ui.colors(primary='#ff6d6d', secondary='#6dffff')
    ui.page_title(f'{navigation_title} | Enigma Scoring Engine')
    with ui.header().classes():
        ui.label('Enigma Scoring Engine').classes('font-bold')
        ui.space()
        with ui.row().classes('items-center'):
            menu()
    yield