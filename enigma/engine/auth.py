import hashlib
from os import urandom
from datetime import datetime, timedelta, timezone

from typing import Annotated

import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, HTTPException, status, Security, APIRouter
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session, select, SQLModel, Field
from pydantic import BaseModel

from engine.database import get_session, db_engine
from engine import secret_key

api_key_header = APIKeyHeader(name='X-API-Key')

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Last 32 of hash bytes are the salt

def get_hash(to_hash: str) -> bytes:
    salt = urandom(32)
    return hashlib.scrypt(
        to_hash.encode('utf-8'), 
        salt=salt, 
        n=16384, 
        r=8, 
        p=1
    ) + salt

def get_hash_from_salt(to_hash: str, salt: bytes) -> bytes:
    return hashlib.scrypt(
        to_hash.encode('utf-8'), 
        salt=salt, 
        n=16384, 
        r=8, 
        p=1
    )

def get_hash_from_salted_hash(from_hash: bytes) -> tuple:
    return (from_hash[:-32], from_hash[-32:])

def verify_hash(plain_pw: str, hashed_pw: bytes) -> bool:
    split_hash = get_hash_from_salted_hash(hashed_pw)
    return get_hash_from_salt(plain_pw, split_hash[1]) == split_hash[0]

# API key auth
class APIKey(SQLModel, table=True):
    __tablename__ = 'apikeys'
    name: str = Field(primary_key=True)
    hash: bytes = Field(nullable=False)

    def __eq__(self, candidate: str):
        return verify_hash(candidate, self.hash)
    
    def __repr__(self):
        return 'APIKey obj with name {} and stored hash'.format(self.name)

    @classmethod
    def new(cls, name: str, api_key: str):
        return cls(
            name=name,
            hash=get_hash(api_key)
        )

async def api_key_auth(api_key: str = Security(api_key_header)):
    with Session(db_engine) as session:
        api_key_hashes = session.exec(select(APIKey)).all()
        for key in api_key_hashes:
            if api_key == key:
                return key.name
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Forbidden'
        )
    
# User auth

permissions_levels = {
    'admin': 0,
    'green': 1,
    'competitor': 2
}

class ParableUser(SQLModel):
    username: str = Field(primary_key=True)
    identifier: int = Field(unique=True)
    permission_level: int = Field(nullable=False)

class ParableUserTable(ParableUser, table=True):
    __tablename__ = 'parableusers'
    pwhash: bytes

class ParableUserCreate(ParableUser):
    password: str = Field(nullable=False)


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None


def authenticate_user(username: str, password: str):
    with Session(db_engine) as session:
        user = session.exec(select(ParableUserTable).where(ParableUserTable.username == username)).one()
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

async def get_current_user(*, session: Session = Depends(get_session), token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
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
    with Session(db_engine) as session:
        user = session.exec(select(ParableUserTable).where(ParableUserTable.username == token_data.username)).one()
    if user is None:
        raise credentials_exception
    return user