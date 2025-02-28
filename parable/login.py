from nicegui import ui, app

from starlette.responses import RedirectResponse

from parable.theme import frame
from parable.auth import get_token, ParableUser

@ui.page('/login')
def login():

    def authenticate():
        if username.value is None or password.value is None:
            ui.notify('Username and password is required', color='negative')
        else:
            token = get_token(username, password)
            if not token:
                ui.notify('Invalid username or password', color='negative')
            else:
                app.storage.user.update({'token': token})

    with frame('Login'):
        with ui.card().classes('absolute-center'):
            username = ui.input('Username').on('keydown.enter', authenticate)
            password = ui.input('Password', password=True, password_toggle_button=True).on('keydown.enter', authenticate)
            ui.button('Log In', on_click=authenticate)

    return None