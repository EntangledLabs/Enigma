from sqlmodel import create_engine, SQLModel, Session

from enigma.engine import postgres_settings

db_engine = create_engine(
    f'postgresql+psycopg://{postgres_settings['user']}:{postgres_settings['password']}@{postgres_settings['host']}:{postgres_settings['port']}/enigma',
    echo=False
)

def init_db():
    from db_models import (
        BoxDB,
        CredlistDB,
        TeamCredsDB,
        InjectDB,
        InjectReportDB,
        ScoreReportDB,
        SLAReportDB,
        RvBTeamDB,
        ParableUserDB,
        SettingsDB
    )
    SQLModel.metadata.create_all(db_engine)

def del_db():
    from db_models import (
        BoxDB,
        CredlistDB,
        TeamCredsDB,
        InjectDB,
        InjectReportDB,
        ScoreReportDB,
        SLAReportDB,
        RvBTeamDB,
        ParableUserDB,
        SettingsDB
    )
    SQLModel.metadata.drop_all(db_engine)