import json

from sqlmodel import SQLModel, Field, Session, select

from enigma.engine.database import db_engine

# Inject
class InjectDB(SQLModel, table=True):
    __tablename__ = 'injects'
    id: int = Field(primary_key=True)
    name: str = Field(unique=True)
    desc: str
    worth: int
    path: str | None = None
    rubric: str

class Inject():

    def __init__(self, id: int, name: str, desc: str, worth: int, path: str | None, rubric: dict):
        self.id = id
        self.name = name
        self.desc = desc
        self.worth = worth
        self.path = path
        self.rubric = rubric
        self.breakdown = self.calculate_score_breakdown()

    def __repr__(self):
        return '<{}> with id {} and name {}'.format(type(self).__name__, self.id, self.name)

    # Calculates the corresponding scores for each scoring category and scoring option
    def calculate_score_breakdown(self):
        breakdown = dict()
        for key in self.rubric.keys():
            weight = self.worth * self.rubric[key]['weight']
            base_cat_score = weight / (len(self.rubric[key]['categories']) - 1)
            possible_cat_scores = dict()
            for i in range(0, len(self.rubric[key]['categories'].keys())):\
                possible_cat_scores.update({
                    list(self.rubric[key]['categories'].keys())[i]: base_cat_score * i
                })
            breakdown.update({
                key: possible_cat_scores
            })
        return breakdown
    
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
        
    # Updates the DB object. If it fails, it returns False, else True
    def update_in_db(self):
        inject_db = InjectDB(
                        id=self.id,
                        name=self.name,
                        desc=self.desc,
                        worth=self.worth,
                        path=self.path,
                        rubric=json.dumps(self.rubric)
                    )
        try:
            with Session(db_engine) as session:
                db_inject = session.exec(select(InjectDB).where(InjectDB.id == self.id)).one()
                db_inject.sqlmodel_update(inject_db)
                session.add(db_inject)
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
class InjectReport(SQLModel, table=True):
    __tablename__ = 'injectreports'
    team_id: int = Field(foreign_key='teams.identifier', primary_key=True)
    inject_num: int = Field(foreign_key='injects.num', primary_key=True)
    score: int
    breakdown: str

    @classmethod
    def get_report(cls, team_id: int, inject_num: int):
        with Session(db_engine) as session:
            db_report = session.exec(
                select(
                    InjectReport
                ).where(
                    InjectReport.team_id == team_id
                ).where(
                    InjectReport.inject_num == inject_num
                )
            ).one()
            return (db_report.score, json.loads(db_report.breakdown))