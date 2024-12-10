import json

from sqlmodel import SQLModel, Field, Session, select

from enigma.engine.database import db_engine

# Score reports
class ScoreReport(SQLModel, table=True):
    __tablename__ = 'scorereports'

    team_id: int = Field(foreign_key='teams.identifier', primary_key=True)
    round: int = Field(primary_key=True)
    score: int
    msg: str

    @classmethod
    def add_to_db(cls, team_id: int, round: int, score: int, msgs: dict):
        with Session(db_engine) as session:
            session.add(
                ScoreReport(
                    team_id=team_id,
                    round=round,
                    score=score,
                    msg=json.dumps(msgs)
                )
            )
            session.commit()