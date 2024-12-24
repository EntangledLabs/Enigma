import secrets, string

from sqlmodel import SQLModel, Field, Session, select

from enigma_models.database import db_engine
from enigma_models.auth import get_hash, verify_hash

# ParableUser model
class ParableUserDB(SQLModel, table=True):
    __tablename__ = 'parableusers'

    name: str = Field(primary_key=True)
    identifier: int = Field(ge=1, le=255, unique=True)
    permission_level: int = Field(ge=0, le=2)
    pw_hash: bytes | None = Field(default=None)

# ParableUser class
class ParableUser:

    def __init__(self, username: str, identifier: int, permission_level: int, pw_hash: bytes=None):
        self.username = username
        self.identifier = identifier
        self.permission_level = permission_level
        self.pw_hash = pw_hash

    def create_pw(self, length: int):
        alphabet = string.ascii_letters + string.digits + '!@#$%^&*'
        password = ''.join(secrets.choice(alphabet) for i in range(length))
        self.pw_hash = get_hash(password)
        return password

    def check_pw(self, password: str):
        return verify_hash(password, self.pw_hash)

    def add_to_db(self):
        try:
            with Session(db_engine) as session:
                session.add(
                    ParableUserDB(
                        name=self.username,
                        identifier=self.identifier,
                        permission_level=self.permission_level,
                        pw_hash=self.pw_hash
                    )
                )
                session.commit()
            return True
        except:
            return False

    def remove_from_db(self) -> bool:
        try:
            with Session(db_engine) as session:
                user = session.exec(
                    select(
                        ParableUserDB
                    ).where(
                        ParableUserDB.name == self.username
                    )
                ).one()
                session.delete(user)
                session.commit()
        except:
            return False
        return True

    @classmethod
    def last_identifier(cls):
        with Session(db_engine) as session:
            last_user = session.exec(
                select(
                    ParableUserDB
                ).order_by(
                    ParableUserDB.identifier.desc()
                )
            ).first()
            if last_user is None:
                return 0
            return last_user.identifier

    @classmethod
    def find(cls, username: str=None, identifier: int=None):
        with Session(db_engine) as session:
            if username is not None:
                user = session.exec(
                    select(
                        ParableUserDB
                    ).where(
                        ParableUserDB.name == username
                    )
                ).one()
            elif identifier is not None:
                user = session.exec(
                    select(
                        ParableUserDB
                    ).where(
                        ParableUserDB.identifier == identifier
                    )
                ).one()

            if user is not None:
                return ParableUser(
                    username=user.name,
                    identifier=user.identifier,
                    permission_level=user.permission_level,
                    pw_hash=user.pw_hash
                )
            return None

    # Fetches all Parable user from the DB
    @classmethod
    def find_all(cls) -> list:
        users = []
        with Session(db_engine) as session:
            db_users = session.exec(
                select(
                    ParableUserDB
                )
            ).all()

        for db_user in db_users:
            users.append(
                ParableUser(
                    username=db_user.name,
                    identifier=db_user.identifier,
                    permission_level=db_user.permission_level,
                    pw_hash=db_user.pw_hash
                )
            )
        return users