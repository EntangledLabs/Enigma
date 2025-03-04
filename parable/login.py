from icecream import ic

import logging

from nicegui import ui, app

from fastapi.requests import Request

from parable.theme import frame
from parable.auth import verify_credentials

log = logging.getLogger('uvicorn')

@ui.page('/login')
def login(request: Request):
    def authenticate():
        log.info(f'Authentication request from {request.client.host}')
        if username.value is None or password.value is None:
            log.info(f'Authentication failed: {'username' if username.value is None else 'password'} not provided')
            ui.notify('Username and password is required', color='negative')
        else:
            user = verify_credentials(username.value, password.value)
            if not user:
                log.warning(f'Login credentials are not correct for username {username.value}')
                ui.notify('Invalid username or password', color='negative')
            else:
                log.info(f'Successful login for user {username.value}')
                app.storage.user.update(
                    {
                        'user': user
                    }
                )
                ui.navigate.to('/dashboard')
                ui.notify('Login successful', color='green')

    with frame('Login'):
        with ui.card().classes('absolute-center'):
            username = ui.input('Username').on('keydown.enter', authenticate)
            password = ui.input('Password', password=True, password_toggle_button=True).on('keydown.enter', authenticate)
            ui.button('Log In', on_click=authenticate)