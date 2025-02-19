from datetime import datetime, timedelta, timezone

import base64
import binascii
import jwt
from jwt.exceptions import InvalidTokenError

from pydantic import BaseModel, Field

from starlette.authentication import AuthCredentials, AuthenticationBackend, AuthenticationError
from starlette.responses import JSONResponse, PlainTextResponse, Response, RedirectResponse
from starlette.exceptions import HTTPException
from starlette.routing import Route

from enigma_models.models.user import ParableUser as ParableUser
from enigma_models.auth import get_hash, get_hash_from_salt, verify_hash

from parable import templates, secret_key, token_age

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

async def login(request):
    template = 'auth/login.html'
    context = {'request': request}
    return templates.TemplateResponse(request, template)

async def logout(request):
    template = 'logout.html'
    context = {'request': request}
    return templates.TemplateResponse(request, template)

async def get_token(request):
    print(request)
    print(request.headers)
    b64credentials = request.headers['Authorization']
    print(b64credentials)
    print(b64credentials.split(' ')[1])
    credentials = base64.b64decode(b64credentials.split(' ')[1]).split(b':')
    print(credentials)
    username = credentials[0].decode()
    pw = credentials[1]
    print(username, pw)

    testusername = 'entangled'
    testpw = 'Cooltech1;'

    if username != testusername:
        return Response(status_code=401)

    hashed_testpw = get_hash(testpw)
    result = verify_hash(plain_pw=pw, hashed_pw=hashed_testpw)
    print(result)
    if not result:
        return Response(status_code=401)

    success_redirect = Response(status_code=200)
    success_redirect.set_cookie(
        key='token',
        value=create_access_token(data={"sub": username}, expires_delta=timedelta(minutes=token_age)),
        httponly=True,
        samesite='strict',
        max_age=token_age
    )

    return success_redirect

def login_required(view):
    pass

# Routes
auth_routes = [
    Route('/login', endpoint=login, methods=['GET']),
    Route('/logout', endpoint=logout, methods=['GET']),
    Route('/token', endpoint=get_token, methods=['POST'])
]