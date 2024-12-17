import json, csv
import random
from os.path import join

from sqlmodel import SQLModel, Field, Session, select

from enigma.enigma_logger import log
from enigma.engine.database import db_engine
from enigma.models.credlist import Credlist, TeamCreds
from enigma.models.settings import Settings
from enigma.models.slareport import SLAReport
from enigma.models.scorereport import ScoreReport
from enigma.models.inject import InjectReport

# Team
class RvBTeamDB(SQLModel, table=True):
    __tablename__ = 'teams'

    name: str = Field(primary_key=True)
    identifier: int = Field(ge=1, le=255, unique=True)
    score: int

class RvBTeam:

    def __init__(self, name: str, identifier: int, services: list[str]):
        self.name = name
        self.identifier = identifier
        self.total_scores = {
            'total_score': 0,
            'raw_score': 0,
            'penalty_score': 0
        }
        self.scores = dict.fromkeys(services, 0)
        self.penalty_scores = dict.fromkeys([f'sla-{service}' for service in services], 0)
        self.sla_tracker = dict.fromkeys(services, 0)
        log.debug(f'Created RvBTeam {self.name}')

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
    def tabulate_scores(self, round: int, reports: dict[str: list[bool, str]]):
        log.debug(f'Compiling score reports and tabulating score for {self.name}')
        print(f'team {self.identifier}')
        msgs = {}
        sla_requirement = Settings.get_setting('sla_requirement')
        # Service check tabulation
        for service, result in reports.items():
            print(service, result)
            log.debug(f'Report: {service} with result {result}')
            msgs.update({
                service: result[1]
            })
            if result[0]:
                # Service check is successful, awards points
                self.award_service_points(service)
                log.debug(f'Awarding points for {service}!')
                if service in self.sla_tracker:
                    self.sla_tracker[service] = 0
                    log.debug(f'Reset SLA tracker for {service}')
            else:
                # Service check is unsuccessful, checking if there is an SLA violation
                if self.sla_tracker.get(service) == 0:
                    # No previous SLA violation tracking, adding service to tracker
                    self.sla_tracker.update({
                        service: 1
                    })
                    log.debug(f'No previous SLA violation, beginning tracking for {service}')
                else:
                    # Previous SLA violating tracking is found, determining if SLA threshold is met
                    if self.sla_tracker.get(service) >= sla_requirement - 1:
                        # Full SLA violation, creating SLA report and deducting points
                        self.award_sla_penalty(service)
                        self.sla_tracker[service] = 0
                        SLAReport(
                            team_id=self.identifier,
                            round=round,
                            service=service
                        ).add_to_db()
                        log.debug(f'SLA violation detected for {service}!')
                    else:
                        # Threshold not met, extending SLA tracker
                        self.sla_tracker[service] = self.sla_tracker[service] + 1
                        log.debug(f'SLA violation tracking extended for {service}')
            print(self.scores)
            print(self.penalty_scores)
            print(self.sla_tracker)

        # Inject tabulation
        inject_reports = InjectReport.get_all_team_reports(self.identifier)
        for inject in inject_reports:
            log.debug(f'Awarding inject points for inject {inject[0]}')
            self.award_inject_points(inject[0], inject[1])

        # Publish score report
        ScoreReport(
            team_id=self.identifier,
            round=round,
            score=self.total_scores['total_score'],
            msg=json.dumps(msgs)
        ).add_to_db()
        log.debug(f'Published score report for team {self.name}')

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
        self.update_in_db()

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
            self.penalty_scores.update({
                sla_str: Settings.get_setting('sla_penalty')
            })
        else:
            self.penalty_scores.update({
                sla_str: (self.penalty_scores.pop(sla_str) + Settings.get_setting('sla_penalty'))
            })
        self.update_total()

    # Things to do with the data
    def export_breakdowns(self, name_fmt: str, path: str):
        self.export_scores_csv(name_fmt, path)

    def export_scores_csv(self, name_fmt: str, path: str):
        log.debug(f'Exporting CSV of scores for {self.name}')
        filepath = join(path, f'{name_fmt}.csv')
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

    # Creates copies of the credlists specific to the team
    def create_credlists(self, credlists: list[Credlist]):
        log.debug(f'Creating credlists for {self.name}')
        for credlist in credlists:
            TeamCreds(
                name=credlist.name,
                team_id=self.identifier,
                creds=json.dumps(credlist.creds)
            ).add_to_db()

    # Returns a random user and password for use in service check
    # Parameter credlists is a list of names of the credlists to choose from
    def get_random_cred(self, credlists: list[str]) -> dict:
        log.debug(f'Getting random cred for {self.name}')
        chosen_list = TeamCreds.fetch_from_db(
            name=random.choice(credlists),
            team_id=self.identifier
        )
        chosen = random.choice(list(chosen_list.items()))
        choice = {
            chosen[0]: chosen[1]
        }
        return choice

    #######################
    # DB fetch/add

    # Tries to add the team object to the DB. If exists, it will return False, else True
    def add_to_db(self):
        log.debug(f'Adding Team {self.name} to database')
        try:
            with Session(db_engine) as session:
                session.add(
                    RvBTeamDB(
                        name=self.name,
                        identifier=self.identifier,
                        score=self.total_scores['total_score']
                    )
                )
                session.commit()
            return True
        except:
            log.warning(f'Failed to add Team {self.name} to database!')
            return False

    # Updates score in DB
    def update_in_db(self):
        log.debug(f'Updating score for Team {self.name} in database')
        with Session(db_engine) as session:
            session.exec(
                select(
                    RvBTeamDB
                ).where(
                    RvBTeamDB.identifier == self.identifier
                )
            ).one().score = self.total_scores['total_score']
            session.commit()

    # Fetches all Team from the DB
    @classmethod
    def find_all(cls, services: list[str]):
        log.debug(f'Retrieving all teams from database')
        teams = []
        with Session(db_engine) as session:
            db_teams = session.exec(
                select(
                    RvBTeamDB
                )
            ).all()
        for db_team in db_teams:
            teams.append(
                RvBTeam(
                    name=db_team.name,
                    identifier=db_team.identifier,
                    services=services
                )
            )
        return teams

    # Creates a new Team from the config info
    @classmethod
    def new(cls, name: str, identifier: int, services: list[str]):
        log.debug(f'Creating new Team {name}')
        return cls(
            name=name,
            identifier=identifier,
            services=services
        )