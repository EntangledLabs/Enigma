from sqlmodel import SQLModel, Field, Session, Relationship
from pydantic import BaseModel

from fastapi import APIRouter, Depends

from typing import List

sla_report_router = APIRouter(
    prefix='/sla-reports',
    tags=['sla-reports'],
    responses={404: {'description': 'Not Found'}}
)
inject_report_router = APIRouter(
    prefix='/inject-reports',
    tags=['inject-reports'],
    responses={404: {'description': 'Not Found'}}
)
score_report_router = APIRouter(
    prefix='/score-reports',
    tags=['score-reports'],
    responses={404: {'description': 'Not Found'}}
)
box_router = APIRouter(
    prefix='/boxes',
    tags=['boxes'],
    responses={404: {'description': 'Not Found'}}
)
team_router = APIRouter(
    prefix='/teams',
    tags=['teams'],
    responses={404: {'description': 'Not Found'}}
)
creds_router = APIRouter(
    prefix='/creds',
    tags=['creds'],
    responses={404: {'description': 'Not Found'}}
)
injects_router = APIRouter(
    prefix='/injects',
    tags=['injects'],
    responses={404: {'description': 'Not Found'}}
)

# Misc
class SettingsTable(SQLModel, table=True):
    __tablename__ = 'settings'
    id: int | None = Field(default=None, primary_key=True)

# Environment info
class BoxTable(SQLModel, table=True):
    __tablename__ = 'boxes'
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    identifier: int = Field(ge=1, le=255, unique=True)
    config: str

class CredlistTable(SQLModel, table=True):
    __tablename__ = 'credlists'
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    creds: str

class InjectTable(SQLModel, table=True):
    __tablename__ = 'injects'
    id: int | None = Field(default=None, primary_key=True)
    num: int = Field(unique=True)
    name: str = Field(unique=True)
    config: str

class TeamTable(SQLModel, table=True):
    __tablename__ = 'teams'
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    identifier: int = Field(ge=1, le=255, unique=True)
    score: int

class TeamCredsTable(SQLModel, table=True):
    __tablename__ = 'teamcreds'
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(foreign_key='credlists.name')
    team_id: int = Field(foreign_key='teams.identifier')
    creds: str

# Reports
class SLAReport(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    team_id: int = Field(foreign_key='teams.identifier')
    round: int
    service: str

class InjectReport(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    team_id: int = Field(foreign_key='teams.identifier')
    inject_num: int = Field(foreign_key='injects.num')
    score: int

class ScoreReport(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    team_id: int = Field(foreign_key='teams.identifier')
    round: int
    score: int

#########
# Collections

class SLAReportCollection(BaseModel):
    injects: List[SLAReport]

    async def add_sla_report():
        pass

    async def list_sla_reports():
        pass

    async def get_sla_report():
        pass

    async def update_sla_report():
        pass

    async def delete_sla_report():
        pass


class InjectReportCollection(BaseModel):
    injects: List[InjectReport]

    async def add_inject_report():
        pass

    async def list_inject_reports():
        pass

    async def get_inject_report():
        pass

    async def update_inject_report():
        pass

    async def delete_inject_report():
        pass

class ScoreReportCollection(BaseModel):
    injects: List[ScoreReport]

    async def add_inject():
        pass

    async def list_injects():
        pass

    async def get_inject():
        pass

    async def update_inject():
        pass

    async def delete_inject():
        pass