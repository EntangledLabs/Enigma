import json

from sqlmodel import SQLModel, Field, Session, select

from enigma.engine.database import db_engine

# Credlist
class CredlistDB(SQLModel, table=True):
    __tablename__ = 'credlists'
    name: str = Field(primary_key=True)
    creds: str

class Credlist():
    
    def __init__(self, name: str, creds: dict):
        self.name = name
        self.creds = creds

    def __repr__(self):
        return '<{}> named {} with creds {}'.format(type(self).__name__, self.name, self.creds)

    # Tries to add the Credlist object to the DB. If exists, it will return False, else True
    def add_to_db(self):
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
            return False

    # Fetches all Credlist from the DB
    @classmethod
    def find_all(cls):
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

    @classmethod
    def add_to_db(cls, name: str, team_id: int, creds: dict):
        with Session(db_engine) as session:
            session.add(
                TeamCreds(
                    name=name,
                    team_id=team_id,
                    creds=json.dumps(creds)
                )
            )
            session.commit()

    @classmethod
    def fetch_from_db(cls, name: str, team_id: int):
        with Session(db_engine) as session:
            db_teamcreds = session.exec(
                select(
                    TeamCreds
                ).where(
                    TeamCreds.name == name
                ).where(
                    TeamCreds.team_id == team_id
                )
            ).one()
            return json.loads(db_teamcreds.creds)