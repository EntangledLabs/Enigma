import json

from sqlmodel import Session, select

from engine.database import db_engine
from enigma.models.models import InjectReportTable

###################################################
# Class Inject
# Represents an inject

class Inject():

    def __init__(self, id: int, name: str, desc: str, worth: int, path: str, rubric: dict):
        self.id = id
        self.name = name
        self.desc = desc
        self.worth = worth
        self.path = path
        self.rubric = rubric
        self.breakdown = self.calculate_score_breakdown()

    def __repr__(self):
        return '<{}> with id {} and name {}'.format(type(self).__name__, self.id, self.name)

    # Calculates the score of an inject and creates a record
    # scores should be in the format {scoring category: score}
    # where 'score' is a str, see the example inject
    # If the record already exists, update the score
    def score_inject(self, team_id: int, scores: dict):
        score = 0
        for cat in self.breakdown.keys():
            score = score + self.breakdown.get(cat).get(scores.get(cat))
        with Session(db_engine) as session:
            inject_report = session.exec(
                select(InjectReportTable).where(
                    InjectReportTable.team_id == team_id
                ).where(InjectReportTable.inject_num == self.id)
            ).one()
            if inject_report is None:
                session.add(
                    InjectReportTable(
                        team_id=team_id,
                        inject_num=self.id,
                        score=score
                    )
                )
                session.commit()
            else:
                inject_report.score = score

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
    
    # Creates a new Inject based on the config info
    @classmethod
    def new(cls, num: int, data: str):
        data = json.loads(data)
        inject = cls(
            id=num,
            name=data['name'],
            desc=data['description'],
            worth=data['worth'],
            path=data['path'],
            rubric=data['rubric']
        )
        return inject