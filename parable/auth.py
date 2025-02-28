from icecream import ic

import logging
from datetime import datetime, timedelta, timezone

from nicegui import app, ui, helpers

from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.routing import APIRouter
from fastapi.requests import Request

from typing import Any, Callable

import base64
import jwt
from jwt.exceptions import InvalidTokenError

from enigma_models.models.user import ParableUser as DBUser
from enigma_models.auth import verify_hash

from parable import secret_key, token_age

log = logging.getLogger('uvicorn')
auth_router = APIRouter()

# Create Bearer tokens
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=10)
    to_encode.update({
        'exp': expire
    })
    return jwt.encode(to_encode, secret_key, algorithm='HS256')

def check_token(payload: dict):
    expiry = datetime.fromtimestamp(int(payload.get("exp")), timezone.utc)
    # If auth token is expired, direct user to login page
    if expiry < datetime.now(timezone.utc):
        return RedirectResponse(url='/auth/login')

    # Issue new token if token is almost expired
    if expiry < datetime.now(timezone.utc) + timedelta(minutes=15):
        pass

# Simple user class to pass around after authentication
class ParableUser:

    def __init__(self, username: str, identifier: int):
        self.username = username
        self.identifier = identifier

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return self.username

# Auth page
class page(ui.page):

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        async def content(request: Request):
            await ui.context.client.connected()

            ic(request)
            ic(request.headers)
            ic(request.cookies)
            auth_token = request.cookies.get("auth_token")
            if auth_token is None:
                ui.navigate.to('/login')
                return

            if helpers.is_coroutine_function(func):
                await func()
            else:
                func()

        return super().__call__(content)

"""# Authentication backend
class ParableAuthBackend(AuthenticationBackend):
    async def authenticate(self, conn):
        token = conn.cookies.get('token')
        if token is None:
            return

        #
        try:
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            username: str = payload.get("sub")
            if username is None:
                raise AuthenticationError('Invalid token, no user provided')
        except InvalidTokenError:
            raise AuthenticationError('Invalid token')

        user = DBUser.find(username=username)
        if user is None:
            raise AuthenticationError('Invalid token, invalid user')

        auth_user = ParableUser(user.username, user.identifier)

        scope = []
        match user.permission_level:
            case user.Permission.ADMINISTRATOR:
                scope.append('admin')
            case user.Permission.GREEN:
                scope.append('green')
            case _:
                scope.append('user')

        auth_credentials = AuthCredentials(scope)

        return auth_credentials, auth_user"""

async def get_token(username, password):
    user = DBUser.find(username=username)
    if user is None:
        log.info(f'Login failed for {username}')
        return False

    result = verify_hash(plain_pw=password, hashed_pw=user.pw_hash)
    if not result:
        log.info(f'Login failed for {username}')
        return False

    log.info(f'Login request for {username} successful, issuing token')

    return create_access_token(data={'sub': username}, expires_delta=timedelta(seconds=token_age))