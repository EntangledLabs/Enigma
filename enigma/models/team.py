import json, csv
import random
from os.path import join

from sqlmodel import SQLModel, Field, Session, select

from enigma.engine.database import db_engine
from enigma.models.credlist import Credlist, TeamCreds
from enigma.models.settings import Settings
from enigma.models.slareport import SLAReport
from enigma.models.scorereport import ScoreReport
from enigma.models.inject import InjectReport

# Team
class TeamDB(SQLModel, table=True):
    __tablename__ = 'teams'

    name: str = Field(primary_key=True)
    identifier: int = Field(ge=1, le=255, unique=True)
    score: int

class Team:

    def __init__(self, name: str, identifier: int, services: list[str], credlists: list[Credlist]):
        self.name = name
        self.identifier = identifier
        self.total_scores = {
            'total_score': 0,
            'raw_score': 0,
            'penalty_score': 0
        }
        self.scores = dict.fromkeys(services, 0)
        self.penalty_scores = dict.fromkeys(services, 0)
        self.sla_tracker = dict.fromkeys(services, 0)

        with Session(db_engine) as session:
            for credlist in credlists:
                session.add(
                    TeamCreds(
                        name=credlist.name,
                        team_id=self.identifier,
                        creds=json.dumps(credlist.creds)
                    )
                )
                session.commit()


    def __repr__(self):
        return '<{}> with team id {} and total score {}'.format(
            type(self).__name__,
            self.identifier,
            self.total_scores['total_score']
        )
    
    #######################
    # Scoring methods

    # Gathers all score reports for a round
    # This should be called at the end of every round
    # Gets passed a dict[service: result]
    def tabulate_scores(self, round: int, reports: dict[str: tuple[bool, str]]):
        msgs = {}
        # Service check tabulation
        for service, result in reports.items():
            msgs.update({
                service: result[1]
            })
            if result[0]:
                # Service check is successful, awards points
                self.award_service_points(service)
                if service in self.sla_tracker:
                    self.sla_tracker.pop(service)
            else:
                # Service check is unsuccessful, checking if there is an SLA violation
                if service not in self.sla_tracker.keys():
                    # No previous SLA violation tracking, adding service to tracker
                    self.sla_tracker.update({
                        service: 1
                    })
                else:
                    # Previous SLA violating tracking is found, determining if SLA threshold is met
                    if self.sla_tracker.get(service) >= Settings.get_setting('sla_requirement') - 1:
                        # Full SLA violation, creating SLA report and deducting points
                        self.award_sla_penalty(service)
                        self.sla_tracker.pop(service)
                        SLAReport.add_to_db(self.identifier, round, service)
                    else:
                        # Threshold not met, extending SLA tracker
                        self.sla_tracker[service] = self.sla_tracker[service] + 1

        # Inject tabulation
        inject_reports = InjectReport.get_all_team_reports(self.identifier)
        for inject in inject_reports:
            self.award_inject_points(inject[0], inject[1])

        # Publish score report
        ScoreReport.add_to_db(self.identifier, round, self.total_scores['total_score'], msgs)

    # Updates total score
    def update_total(self):
        total = 0
        for service, points in self.scores.items():
            total = total + points
        self.total_scores['raw_score'] = total

        total = 0
        for penalty, points in self.penalty_scores.items():
            total = total + points
        self.total_scores['penalty_score'] = total

        self.total_scores['total_score'] = self.total_scores['raw_score'] - self.total_scores['penalty_score']
        with Session(db_engine) as session:
            session.exec(
                select(
                    TeamDB
                ).where(
                    TeamDB.identifier == self.identifier
                )
            ).one().score = self.total_scores['total_score']
            session.commit()

    # Service adding/removal
    def add_service(self, name: str):
        self.scores.update({
            name: 0
        })

    def remove_service(self, name: str):
        if name not in self.scores.keys():
            return
        self.scores.pop(name)
        self.update_total()

    # Point awarding
    def award_service_points(self, service: str):
        if service not in self.scores.keys():
            self.add_service(service)
        self.scores.update({
            service: (self.scores.pop(service) + Settings.get_setting('check_points'))
        })
        self.update_total()

    def award_inject_points(self, inject_num: int, points: int):
        inject_str = f'inject{inject_num}'
        self.scores.update({
            inject_str: points
        })
        self.update_total()
    
    # Point deductions
    def award_sla_penalty(self, service: str):
        sla_str = f'sla-{service}'
        if sla_str not in self.penalty_scores.keys():
            with Session(db_engine) as session:
                self.penalty_scores.update({
                    sla_str: Settings.get_setting('sla_penalty')
                })
        else:
            with Session(db_engine) as session:
                self.penalty_scores.update({
                    sla_str: (self.penalty_scores.pop(sla_str) + Settings.get_setting('sla_penalty'))
                })
        self.update_total()

    # Things to do with the data
    def export_scores_csv(self, name: str, path: str):
        filepath = join(path, f'{name}.csv')
        fieldnames = [
            'point_category',
            'raw_points',
            'penalty_points',
            'total_points'
        ]

        with open(filepath, 'w+', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerow({
                fieldnames[0]: 'total',
                fieldnames[1]: self.total_scores['raw_score'],
                fieldnames[2]: self.total_scores['penalty_score'],
                fieldnames[3]: self.total_scores['total_score']
            })
            
            rows = list()

            for cat in sorted(self.scores.keys()):
                row = {
                    fieldnames[0]: cat,
                    fieldnames[1]: self.scores.get(cat),
                    fieldnames[2]: 0,
                    fieldnames[3]: 0
                }
                rows.append(row)

            for cat, val in self.penalty_scores.items():
                pfield = cat.split('-')
                if len(pfield) == 2:
                    pfield = pfield[1]
                else:
                    pfield = pfield[0]

                for i in range(0, len(rows)):
                    if rows[i][fieldnames[0]] == pfield:
                        rows[i].update({
                            fieldnames[2]: val
                        })
            
            for i in range(0, len(rows)):
                rows[i].update({
                    fieldnames[3]: (rows[i][fieldnames[1]] - rows[i][fieldnames[2]])
                })

            for row in rows:
                writer.writerow(row)

    #######################
    # Creds methods

    # Returns a random user and password for use in service check
    # Parameter credlists is a list of names of the credlists to choose from
    def get_random_cred(self, credlists: list[str]) -> dict:
        with Session(db_engine) as session:
            chosen_list = json.loads(
                session.exec(
                    select(
                        TeamCreds
                    ).where(
                        TeamCreds.name == random.choice(credlists)
                    ).where(
                        TeamCreds.team_id == self.identifier
                    )
                ).one().creds
            )
        chosen = random.choice(list(chosen_list.items()))
        choice = {
            chosen[0]: chosen[1]
        }
        return choice

    # Creates a new Team from the config info
    @classmethod
    def new(cls, services: list[str], data: dict):
        return cls(
            name=data['name'],
            identifier=data['identifier'],
            services=services,
            credlists=data['credlists']
        )