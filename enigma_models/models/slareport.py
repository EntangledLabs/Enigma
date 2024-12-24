from sqlmodel import SQLModel, Field, Session

from enigma_models.database import db_engine

# SLA Report
class SLAReportDB(SQLModel, table=True):
    __tablename__ = 'slareports'

    team_id: int = Field(foreign_key='teams.identifier', primary_key=True)
    round: int = Field(primary_key=True)
    service: str = Field(primary_key=True)

# SLA Report
class SLAReport:

    def __init__(self, team_id: int, round: int, service: str):
        self.team_id = team_id
        self.round = round
        self.service = service

    #######################
    # DB fetch/add

    def add_to_db(self):
        with Session(db_engine) as session:
            session.add(
                SLAReportDB(
                    team_id=self.team_id,
                    round=self.round,
                    service=self.service
                )
            )
            session.commit()