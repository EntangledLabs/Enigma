import hashlib
from os import urandom

from fastapi import Depends, HTTPException, status, Security
from fastapi.security import APIKeyHeader

from sqlmodel import Session, select, SQLModel, Field

from engine.database import db_engine

api_key_header = APIKeyHeader(name='X-API-Key')

# Auth
class APIKey(SQLModel, table=True):
    __tablename__ = 'apikeys'
    name: str = Field(primary_key=True)
    hash: bytes = Field(nullable=False)
    salt: bytes = Field(nullable=False)

    def __eq__(self, candidate: str):
        return hashlib.scrypt(
            candidate.encode('utf-8'), 
            salt=self.salt, 
            n=16384, 
            r=8, 
            p=1
        ) == self.hash
    
    def __repr__(self):
        return 'APIKey obj with name {} and stored hash'.format(self.name)

    @classmethod
    def new(cls, name: str, api_key: str):
        salt = urandom(32)
        return cls(
            name=name,
            hash=hashlib.scrypt(
                api_key.encode('utf-8'),
                salt=salt,
                n=16384, 
                r=8, 
                p=1
            ),
            salt=salt
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