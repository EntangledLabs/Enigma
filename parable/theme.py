from contextlib import contextmanager

from .menu import menu

from nicegui import ui

@contextmanager
def frame(navigation_title: str):
    ui.colors()
    with ui.header():
        pass