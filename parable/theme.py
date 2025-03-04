from contextlib import contextmanager

from .menu import menu

from nicegui import ui

@contextmanager
def frame(navigation_title: str):
    ui.colors()
    ui.page_title(f'{navigation_title} | Enigma Scoring Engine')
    with ui.header():
        pass

    yield