from sqlmodel import SQLModel, Field, Session, select

from enigma_models.database import db_engine

# Score reports model
class ScoreReportDB(SQLModel, table=True):
    __tablename__ = 'scorereports'

    team_id: int = Field(foreign_key='teams.identifier', primary_key=True)
    round: int = Field(primary_key=True)
    score: int
    msg: str

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
        try:
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
            return True
        except:
            return False