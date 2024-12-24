import json

from sqlmodel import SQLModel, Field, Session, select

from enigma_models.database import db_engine

# Inject model
class InjectDB(SQLModel, table=True):
    __tablename__ = 'injects'

    id: int = Field(primary_key=True)
    name: str = Field(unique=True)
    desc: str
    worth: int
    path: str | None = None
    rubric: str

# InjectReport model
class InjectReportDB(SQLModel, table=True):
    __tablename__ = 'injectreports'

    team_id: int = Field(foreign_key='teams.identifier', primary_key=True)
    inject_num: int = Field(foreign_key='injects.id', primary_key=True)
    score: int
    breakdown: str

# Inject class
class Inject:

    def __init__(self, id: int, name: str, desc: str, worth: int, path: str | None, rubric: dict):
        self.id = id
        self.name = name
        self.desc = desc
        self.worth = worth
        self.path = path
        self.rubric = rubric

    #######################
    # DB fetch/add

    # Tries to add the inject object to the DB. If exists, it will return False, else True
    def add_to_db(self):
        try:
            with Session(db_engine) as session:
                session.add(
                    InjectDB(
                        id=self.id,
                        name=self.name,
                        desc=self.desc,
                        worth=self.worth,
                        path=self.path,
                        rubric=json.dumps(self.rubric)
                    )
                )
                session.commit()
                return True
        except:
            return False

    # Fetches all Inject from the DB
    @classmethod
    def find_all(cls):
        injects = []
        with Session(db_engine) as session:
            db_injects = session.exec(select(InjectDB)).all()
            for inject in db_injects:
                injects.append(
                    Inject.new(
                        id=inject.id,
                        name=inject.name,
                        desc=inject.desc,
                        worth=inject.worth,
                        path=inject.path,
                        rubric=json.loads(inject.rubric)
                    )
                )
        return injects

    # Creates an Inject object based off of DB data
    @classmethod
    def new(cls, id: int, name: str, desc: str, worth: int, path: str | None, rubric: str):
        return cls(
            id=id,
            name=name,
            desc=desc,
            worth=worth,
            path=path,
            rubric=json.loads(rubric)
        )

# Inject reports
class InjectReport:
    def __init__(self, team_id: int, inject_num: int, score: int, breakdown: str):
        self.team_id = team_id
        self.inject_num = inject_num
        self.score = score
        self.breakdown = breakdown

    #######################
    # DB fetch/add

    # Tries to add the inject report object to the DB. If exists, it will return False, else True
    def add_to_db(self):
        try:
            with Session(db_engine) as session:
                session.add(
                    InjectReportDB(
                        team_id=self.team_id,
                        inject_num=self.inject_num,
                        score=self.score,
                        breakdown=self.breakdown
                    )
                )
                session.commit()
                return True
        except:
            return False

    @classmethod
    def get_report(cls, team_id: int, inject_num: int) -> tuple[int, dict]:
        with Session(db_engine) as session:
            db_report = session.exec(
                select(
                    InjectReportDB
                ).where(
                    InjectReportDB.team_id == team_id
                ).where(
                    InjectReportDB.inject_num == inject_num
                )
            ).one()
            return db_report.score, json.loads(db_report.breakdown)

    @classmethod
    def get_all_team_reports(cls, team_id: int)-> list[tuple[int, int]]:
        with Session(db_engine) as session:
            db_reports = session.exec(
                select(
                    InjectReportDB
                ).where(
                    InjectReportDB.team_id == team_id
                )
            ).all()
            return [(db_report.inject_num, db_report.score) for db_report in db_reports]