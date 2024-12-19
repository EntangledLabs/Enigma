from sqlmodel import Session

from enigma.logger import log
from enigma.engine.database import db_engine

from db_models import ScoreReportDB

# Score reports
class ScoreReport:
    def __init__(self, team_id: int, round: int, score: int, msg: str):
        self.team_id = team_id
        self.round = round
        self.score = score
        self.msg = msg

    #######################
    # DB fetch/add

    def add_to_db(self):
        log.debug(f'Adding score report to database for team {self.team_id} during round {self.round}')
        with Session(db_engine) as session:
            session.add(
                ScoreReportDB(
                    team_id=self.team_id,
                    round=self.round,
                    score=self.score,
                    msg=self.msg
                )
            )
            session.commit()