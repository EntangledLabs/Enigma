from sqlmodel import SQLModel, Field, Session

from enigma.enigma_logger import log
from enigma.engine.database import db_engine

# SLA Report
class SLAReport(SQLModel, table=True):
    __tablename__ = 'slareports'

    team_id: int = Field(foreign_key='teams.identifier', primary_key=True)
    round: int = Field(primary_key=True)
    service: str = Field(primary_key=True)

    #######################
    # DB fetch/add

    def add_to_db(self):
        log.debug(f'Adding SLAReport for team {self.team_id} during round {self.round}')
        with Session(db_engine) as session:
            session.add(
                self
            )
            session.commit()