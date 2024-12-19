from sqlmodel import Session

from enigma.logger import log
from enigma.engine.database import db_engine

from db_models import SLAReportDB

# SLA Report
class SLAReport:

    def __init__(self, team_id: int, round: int, service: str):
        self.team_id = team_id
        self.round = round
        self.service = service

    #######################
    # DB fetch/add

    def add_to_db(self):
        log.debug(f'Adding SLAReport for team {self.team_id} during round {self.round}')
        with Session(db_engine) as session:
            session.add(
                SLAReportDB(
                    team_id=self.team_id,
                    round=self.round,
                    service=self.service
                )
            )
            session.commit()