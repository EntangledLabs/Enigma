from sqlmodel import SQLModel, Field, Session

from enigma.enigma_logger import log
from enigma.engine.database import db_engine

# Score reports
class ScoreReport(SQLModel, table=True):
    __tablename__ = 'scorereports'

    team_id: int = Field(foreign_key='teams.identifier', primary_key=True)
    round: int = Field(primary_key=True)
    score: int
    msg: str

    #######################
    # DB fetch/add

    def add_to_db(self):
        log.debug(f'Adding score report to database for team {self.team_id} during round {self.round}')
        with Session(db_engine) as session:
            session.add(
                self
            )
            session.commit()