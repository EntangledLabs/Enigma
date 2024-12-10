import json

from sqlmodel import SQLModel, Field, Session, select

from enigma.engine.database import db_engine

# SLA Report
class SLAReport(SQLModel):
    __tablename__ = 'slareports'

    team_id: int = Field(foreign_key='teams.identifier', primary_key=True)
    round: int = Field(primary_key=True)
    service: str

    @classmethod
    def add_to_db(cls, team_id: int, round: int, service: str):
        with Session(db_engine) as session:
            session.add(
                SLAReport(
                    team_id=team_id,
                    round=round,
                    service=service
                )
            )
            session.commit()