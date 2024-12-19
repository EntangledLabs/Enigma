import json

from sqlmodel import Session, select

from enigma.engine.database import db_engine
from enigma.logger import log

from db_models import InjectDB, InjectReportDB

# Inject
class Inject:

    def __init__(self, id: int, name: str, desc: str, worth: int, path: str | None, rubric: dict):
        self.id = id
        self.name = name
        self.desc = desc
        self.worth = worth
        self.path = path
        self.rubric = rubric
        self.breakdown = self.calculate_score_breakdown()
        log.debug(f"Created new Inject with name {self.name}")

    def __repr__(self):
        return '<{}> with id {} and name {}'.format(type(self).__name__, self.id, self.name)

    # Calculates the corresponding scores for each scoring category and scoring option
    def calculate_score_breakdown(self):
        log.debug(f"Calculating score breakdown for Inject {self.name}")
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

    #######################
    # DB fetch/add

    # Tries to add the inject object to the DB. If exists, it will return False, else True
    def add_to_db(self):
        log.debug(f"Adding Inject {self.name} to database")
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
            log.warning(f"Failed to add Inject {self.name} to database!")
            return False

    # Fetches all Inject from the DB
    @classmethod
    def find_all(cls):
        log.debug(f"Finding all Injects")
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
        log.debug(f"Creating new Inject {name}")
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

    @classmethod
    def get_report(cls, team_id: int, inject_num: int) -> tuple[int, dict]:
        log.debug(f"Finding InjectReport for team {team_id} with inject number {inject_num}")
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
            return (db_report.score, json.loads(db_report.breakdown))

    @classmethod
    def get_all_team_reports(cls, team_id: int)-> list[tuple[int, int]]:
        log.debug(f"Finding all InjectReport for team {team_id}")
        with Session(db_engine) as session:
            db_reports = session.exec(
                select(
                    InjectReportDB
                ).where(
                    InjectReportDB.team_id == team_id
                )
            ).all()
            return [(db_report.inject_num, db_report.score) for db_report in db_reports]