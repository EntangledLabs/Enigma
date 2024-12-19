import secrets, string

from sqlmodel import Session, select

from db_models import ParableUserDB
from db_models.auth import get_hash

from praxos.logger import log
from praxos.database import db_engine

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

    def add_to_db(self):
        log.debug(f"Adding Parable user {self.username} to DB")
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
            log.warning(f"Failed to add Parable user {self.username} to DB")
            return False

    def remove_from_db(self) -> bool:
        log.debug(f'Removing Parable user {self.username} from database')
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
            log.warning(f'Failed to remove Parable user {self.name} from database!')
            return False
        return True

    @classmethod
    def last_identifier(cls):
        with Session(db_engine) as session:
            log.debug(f'Retrieving last identifier from database')
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

    # Fetches all Parable user from the DB
    @classmethod
    def find_all(cls) -> list:
        log.debug(f'Retrieving all Parable users from database')
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