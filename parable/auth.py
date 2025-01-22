from datetime import datetime, timedelta, timezone

import binascii
import jwt
from jwt.exceptions import InvalidTokenError

from pydantic import BaseModel, Field

from starlette.authentication import AuthCredentials, AuthenticationBackend, AuthenticationError
from starlette.responses import JSONResponse, PlainTextResponse, Response
from starlette.exceptions import HTTPException

from enigma_models.models.user import ParableUser as ParableUser
from enigma_models.auth import get_hash, get_hash_from_salted_hash, get_hash_from_salt, verify_hash

from parable.route import ParableRouter
from parable import templates, secret_key

# Bearer token auth
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

def authenticate_user(username: str, password: str):
    user = ParableUser.find(username=username)
    if not user:
        return False
    if not verify_hash(password, user.pwhash):
        return False
    return user

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

async def get_current_user(token: str):
    credentials_exception = HTTPException(
        status_code=401,
        detail='Credentials could not be validated',
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = ParableUser.find(username=username)
    if user is None:
        raise credentials_exception
    return user

# Authentication backend
class ParableAuthBackend(AuthenticationBackend):
    async def authenticate(self, conn):
        if "Authorization" not in conn.headers:
            return

        auth = conn.headers["Authorization"]
        try:
            scheme, credentials = auth.split()
            if scheme.lower() != "basic":
                return
        except (ValueError, UnicodeDecodeError, binascii.Error) as exc:
            raise AuthenticationError('Invalid auth credentials')

# Authentication routes
auth_routes = ParableRouter('auth')

@auth_routes.route('/login', methods=['GET'])
async def login(request):
    template = 'auth/login.html'
    context = {'request': request}
    return templates.TemplateResponse(request, template)

@auth_routes.route('/logout', methods=['GET'])
async def logout(request):
    template = 'logout.html'
    context = {'request': request}
    return templates.TemplateResponse(request, template)

@auth_routes.route('/token', methods=['POST'])
async def get_token(scope, receive, send):
    print(scope, receive, send)
    assert scope['type'] == 'http'
    response = JSONResponse({'ok': True})
    await response(scope, receive, send)

def login_required(view):
    pass