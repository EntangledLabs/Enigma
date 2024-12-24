from sqlmodel import create_engine, SQLModel, Session

from enigma_models import postgres_settings

db_engine = create_engine(
    f'postgresql+psycopg://{postgres_settings['competitor']}:{postgres_settings['password']}@{postgres_settings['host']}:{postgres_settings['port']}/enigma',
    echo=False
)

def init_db():
    from enigma_models.models.box import BoxDB
    from enigma_models.models.credlist import CredlistDB, TeamCredsDB
    from enigma_models.models.inject import InjectDB, InjectReportDB
    from enigma_models.models.scorereport import ScoreReportDB
    from enigma_models.models.settings import SettingsDB
    from enigma_models.models.slareport import SLAReportDB
    from enigma_models.models.team import RvBTeamDB
    from enigma_models.models.user import ParableUserDB

    SQLModel.metadata.create_all(db_engine)

def del_db():
    from enigma_models.models.box import BoxDB
    from enigma_models.models.credlist import CredlistDB, TeamCredsDB
    from enigma_models.models.inject import InjectDB, InjectReportDB
    from enigma_models.models.scorereport import ScoreReportDB
    from enigma_models.models.settings import SettingsDB
    from enigma_models.models.slareport import SLAReportDB
    from enigma_models.models.team import RvBTeamDB
    from enigma_models.models.user import ParableUserDB

    SQLModel.metadata.drop_all(db_engine)