from nicegui import ui, app

from parable.theme import frame

@ui.page('/')
def index():
    with frame('Home Page'):
        ui.label('Welcome to Enigma!')