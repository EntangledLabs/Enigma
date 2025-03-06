import logging

from nicegui import app, ui, helpers

from fastapi.routing import APIRouter

from typing import Any, Callable

from enigma_models.models.user import ParableUser as DBUser, ParablePermission
from enigma_models.auth import verify_hash

log = logging.getLogger('uvicorn')
auth_router = APIRouter()

# Class ParableUser keeps most of the properties of ParableUser from enigma_models but doesn't keep the pw hash in memory
class ParableUser:

    def __init__(self, username: str, identifier: int, permission_level: ParablePermission):
        self.username = username
        self.identifier = identifier
        self.permission_level = permission_level

# Auth page
class auth_page(ui.page):

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        async def content():
            await ui.context.client.connected()
            user = app.storage.user.get('user')
            if user is None:
                ui.navigate.to('/login')

            if helpers.is_coroutine_function(func):
                await func()
            else:
                func()

        return super().__call__(content)

# Admin page
class admin_page(ui.page):
    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        async def content():
            await ui.context.client.connected()
            user = app.storage.user.get('user')
            if user is None:
                ui.navigate.to('/login')

            if not user.get('permission_level') == ParablePermission.ADMINISTRATOR:
                ui.navigate.to('/login')
                ui.timer(1.0, lambda: ui.notify('You cannot access this page!', color='negative'))

            if helpers.is_coroutine_function(func):
                await func()
            else:
                func()

        return super().__call__(content)

def verify_credentials(username, password) -> bool | dict:
    user = DBUser.find(username=username)
    if user is None:
        log.info(f'Username not found: {username}')
        return False

    result = verify_hash(plain_pw=password, hashed_pw=user.pw_hash)
    if not result:
        log.info(f'Password verification failed for user {username}')
        return False

    log.info(f'Login request for {username} successful')

    return {
        'username': username,
        'identifier': user.identifier,
        'permission_level': user.permission_level,
    }
