from sqlmodel import create_engine, SQLModel, Session

from enigma.engine import postgres_settings

db_engine = create_engine(
    f'postgresql+psycopg://{postgres_settings['user']}:{postgres_settings['password']}@{postgres_settings['host']}:{postgres_settings['port']}/enigma',
    echo=False
)

def get_session():
    with Session(db_engine) as session:
        yield session

def init_db():
    from enigma.models import (
        box,
        credlist,
        inject,
        scorereport,
        settings,
        slareport,
        team
    )
    SQLModel.metadata.create_all(db_engine)

def del_db():
    from enigma.models import (
        box,
        credlist,
        inject,
        scorereport,
        settings,
        slareport,
        team
    )
    SQLModel.metadata.drop_all(db_engine)