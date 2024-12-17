import json

from sqlmodel import SQLModel, Field, Session, select

from enigma.engine.database import db_engine
from enigma.enigma_logger import log


# Credlist
class CredlistDB(SQLModel, table=True):
    __tablename__ = 'credlists'
    name: str = Field(primary_key=True)
    creds: str

class Credlist:
    
    def __init__(self, name: str, creds: dict):
        self.name = name
        self.creds = creds
        log.debug(f"Created new Credlist with name {self.name}")

    def __repr__(self):
        return '<{}> named {} with creds {}'.format(type(self).__name__, self.name, self.creds)

    # Tries to add the Credlist object to the DB. If exists, it will return False, else True
    def add_to_db(self):
        log.debug(f"Adding credlist {self.name} to database")
        try:
            with Session(db_engine) as session:
                session.add(
                    CredlistDB(
                        name=self.name,
                        creds=json.dumps(self.creds)
                    )
                )
                session.commit()
            return True
        except:
            log.warning(f"Failed to add Credlist {self.name} to database!")
            return False

    #######################
    # DB fetch/add

    # Fetches all Credlist from the DB
    @classmethod
    def find_all(cls):
        log.debug(f"Retrieving all Credlists from database")
        credlists = []
        with Session(db_engine) as session:
            db_credlists = session.exec(select(CredlistDB)).all()
            for credlist in db_credlists:
                credlists.append(
                    Credlist.new(
                        name=credlist.name,
                        creds=credlist.creds
                    )
                )
        return credlists

    # Creates a Credlist object based off of DB data
    @classmethod
    def new(cls, name: str, creds: str):
        log.debug(f"Creating new Credlist with name {name}")
        return cls(
            name=name,
            creds=json.loads(creds)
        )
    
# TeamCreds
class TeamCreds(SQLModel, table=True):
    __tablename__ = 'teamcreds'

    name: str = Field(foreign_key='credlists.name', primary_key=True)
    team_id: int = Field(foreign_key='teams.identifier', primary_key=True)
    creds: str

    #######################
    # DB fetch/add

    def add_to_db(self) -> bool:
        log.debug(f"Adding team creds to database for team with ID {self.team_id}")
        try:
            with Session(db_engine) as session:
                session.add(
                    self
                )
                session.commit()
            return True
        except:
            log.warning(f"Failed to add team creds for team with ID {self.team_id}!")
            return False

    @classmethod
    def fetch_from_db(cls, name: str, team_id: int):
        log.debug(f"Fetching team creds for team with ID {team_id}")
        with Session(db_engine) as session:
            db_teamcred = session.exec(
                select(
                    TeamCreds
                ).where(
                    TeamCreds.name == name
                ).where(
                    TeamCreds.team_id == team_id
                )
            ).one()
            return json.loads(db_teamcred.creds)

    @classmethod
    def fetch_all(cls, team_id: int):
        log.debug(f"Fetching all team creds for team with ID {team_id}")
        with Session(db_engine) as session:
            db_teamcreds = session.exec(
                select(
                    TeamCreds
                ).where(
                    TeamCreds.team_id == team_id
                )
            ).all()
            return [teamcreds.creds for teamcreds in db_teamcreds]