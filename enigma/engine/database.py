from sqlmodel import create_engine, SQLModel, Session

from enigma.engine import db_url

db_engine = create_engine(db_url, echo=False)

def get_session():
    with Session(db_engine) as session:
        yield session

def init_db():
    from enigma.models import (
        box,
        credlist,
        inject,
        injectreport,
        scorereport,
        settings,
        slareport,
        team,
        teamcreds
    )
    SQLModel.metadata.create_all(db_engine)

def del_db():
    from enigma.models import (
        box,
        credlist,
        inject,
        injectreport,
        scorereport,
        settings,
        slareport,
        team,
        teamcreds
    )
    SQLModel.metadata.drop_all(db_engine)