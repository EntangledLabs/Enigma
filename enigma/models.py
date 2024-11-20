from sqlalchemy import Column, Integer, Text, TypeDecorator, Uuid, ForeignKey, Boolean
from sqlalchemy.orm import validates

from enigma.database import Base
from enigma.auth import PWHash

import secrets, string, logging

log = logging.getLogger(__name__)

## Custom SQLAlchemy Types

class PasswordHash(TypeDecorator):
    impl = Text
    cache_ok = False

    def __init__(self, **kwds):
        super(PasswordHash, self).__init__(**kwds)

    def process_bind_param(self, value, dialect):
        return self._convert(value).combined()
    
    def process_result_value(self, value, dialect):
        if value is not None:
            return self._convert(value)

    def validator(self, password):
        return self._convert(password)
    
    def _convert(self, value):
        log.debug('sqlalchemy is conducting PWHash operations')
        if isinstance(value, PWHash):
            return value
        elif isinstance(value, str):
            return PWHash(value[:-32], value[-32:])
        elif isinstance(value, bytes):
            return PWHash(value[:-32], value[-32:])
        elif value is not None:
            log.error('couldn\'t convert a {} to a PWHash'.format(value))

## Models

class Team(Base):
    __tablename__ = 'teams'
    id = Column(Integer, primary_key=True)
    username = Column(Text, unique=True, nullable=False)
    pw_hash = Column(PasswordHash, nullable=False)
    identifier = Column(Integer, nullable=False)
    score = Column(Integer, nullable=False)

    def __repr__(self):
        return '<Team> object for {} with id {}, identifier {}, and total score {}'.format(
            self.username, self.id, self.identifier, self.score
        )

    @validates('pw_hash')
    def _validate_password(self, key, password):
        return getattr(type(self), key).type.validator(password)

    def authenticate(self, pw):
        log.debug('authenticating password for {}'.format(self.username))
        return self.pw_hash == pw

    @classmethod
    def generate_password(cls):
        log.debug('creating a password')
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for i in range(16))

class TeamCreds(Base):
    __tablename__ = 'credlists'
    name = Column(Text, primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    creds = Column(Text, nullable=False)

    def __repr__(self):
        return f'<TeamCreds> object with name {self.name} belonging to team {self.team_id}'

class Inject(Base):
    __tablename__ = 'injects'
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    desc = Column(Text)
    file = Column(Text)

class ScoreReport(Base):
    __tablename__ = 'scorereports'
    id = Column(Uuid, primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    round = Column(Integer, nullable=False)
    service = Column(Text, nullable=False)
    result = Column(Boolean, nullable=False)

class SLAReport(Base):
    __tablename__ = 'slareports'
    id = Column(Uuid, primary_key = True)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    round = Column(Integer, nullable=False)
    service = Column(Text, nullable=False)

class InjectReport(Base):
    __tablename__ = 'injectreports'
    id = Column(Uuid, primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.id'))
    inject_num = Column(Integer, ForeignKey('injects.id'), nullable=False)
    score = Column(Integer, nullable=False)