from os import listdir
from os.path import join, splitext, isfile
import tomllib, csv, json
import random

from fastapi import Depends
from sqlmodel import Session, select

import tomli_w

from engine.database import db_engine
from engine.checks import Service
from engine.settings import boxes_path, creds_path, injects_path
from engine.models import InjectReport, SLAReport, ScoreReport, Settings
from engine.models import TeamCredsTable, TeamTable, BoxTable, InjectTable, CredlistTable

###################################################
# Class Box
# Represents a box and its services

class Box():

    def __init__(self, name: str, identifier: int, services: list[Service]):
        self.name = name
        self.identifier = identifier
        self.services = services

    def __repr__(self):
        return '<{}> named \'{}\' with services {}'.format(type(self).__name__, self.name, self.services)
    
    # Get every service for the box in the format 'box.service'
    def get_service_names(self):
        names = list()
        for service in self.services:
            names.append(f'{self.name}.{service.name}')
        return names

    # Takes a dict of service config data and creates new Service objects based off of them
    @classmethod
    def compile_services(cls, data: dict):
        services = list()
        for service in Service.__subclasses__():
            if service.name in data:
                services.append(service.new(data[service.name]))
        return services
    
    # Performs get_service_names() for every box in the list
    @classmethod
    def full_service_list(cls, boxes: list):
        services = list()
        for box in boxes:
            services.extend(box.get_service_names())
        return services

    # Creates a new Box object from a config file or string
    @classmethod
    def new(cls, name:str, data: str):
        data = tomllib.loads(data)
        box = cls(
            name=name,
            identifier=data['identifier'],
            services=cls.compile_services(data)
        )
        return box

###################################################
# Credlist class
# Holds a credlist and its name

class Credlist():
    
    def __init__(self, name: str, creds: dict):
        self.name = name
        self.creds = creds

    def __repr__(self):
        return '<{}> named {} with creds {}'.format(type(self).__name__, self.name, self.creds)

    @classmethod
    def new(cls, data: dict):
        return cls(
            name = data['name'],
            creds = data['creds']
        )

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
                select(InjectReport).where(
                    InjectReport.team_id == team_id
                ).where(InjectReport.inject_num == self.id)
            ).one()
            if inject_report is None:
                session.add(
                    InjectReport(
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
        data = tomllib.loads(data)
        inject = cls(
            num=num,
            name=data['name'],
            desc=data['description'],
            worth=data['worth'],
            path=data['path'],
            rubric=data['rubric']
        )
        return inject

###################################################
# Class Team
# Keeps a team's score breakdown and cred lists in one place

class Team():

    def __init__(self, name: str, identifier: int, services: list[str], credlists: list[Credlist]):
        self.name = name
        self.identifier = identifier
        self.total_scores = {
            'total_score': 0,
            'raw_score': 0,
            'penalty_score': 0
        }
        self.scores = dict.fromkeys(services, 0)
        self.penalty_scores = {}
        self.sla_tracker = {}

        with Session(db_engine) as session:
            for credlist in credlists:
                session.add(
                    TeamCredsTable(
                        name=credlist.name,
                        team_id=self.identifier,
                        creds=json.dumps(credlist.creds)
                    )
                )
            session.commit()

    def __repr__(self):
        return '<{}> with team id {}, scores object {}, and credlist with {}'.format(
            type(self).__name__,
            self.id,
            self.scores['total_score'],
            self.credlists
        )
    
    #######################
    # Scoring methods


    # Gathers all score reports for a round
    # This should be called at the end of every round
    # Gets passed a dict[service: result]
    def tabulate_scores(self, round: int, reports: dict):
        # Service check tabulation
        for service, result in reports.items():
            if result:
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
                    with Session(db_engine) as session:
                        if self.sla_tracker.get(service) == session.exec(select(Settings)).one().sla_requirement - 1:
                            # Full SLA violation, creating SLA report and deducting points
                            self.award_sla_penalty(service)
                            self.sla_tracker.pop(service)
                            session.add(
                                SLAReport(
                                    team_id = self.identifier,
                                    round = round,
                                    service = service
                                )
                            )
                            session.commit()
                        else:
                            # Threshold not met, extending SLA tracker
                            self.sla_tracker.update({
                                service: self.sla_tracker.pop(service) + 1
                            })

        # Inject tabulation
        with Session(db_engine) as session:
            inject_reports = session.exec(
                select(InjectReport).where(
                    InjectReport.team_id == self.identifier
                )
            ).all()
        for inject in inject_reports:
            if f'inject{inject.inject_num}' in self.scores and self.scores[f'inject{inject.inject_num}'] == inject.score:
                continue
            else:
                self.award_inject_points(inject.inject_num, inject.score)

        # Publish score report
        with Session(db_engine) as session:
            session.add(
                ScoreReport(
                    team_id = self.identifier,
                    round = round,
                    score = self.total_scores['total_score']
                )
            )
            session.commit()

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
                select(TeamTable).where(
                    TeamTable.identifier == self.identifier
                )
            ).one().score = self.total_scores['total_score']
            session.commit()

    # Service adding/removal
    def add_service(self, name: str):
        if name in self.scores.keys():
            return
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
            return
        with Session(db_engine) as session:
            self.scores.update({
                service: (self.scores.pop(service) + session.exec(select(Settings)).one().check_points)
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
                    sla_str: session.exec(select(Settings)).one().sla_penalty
                })
        else:
            with Session(db_engine) as session:
                self.penalty_scores.update({
                    sla_str: (self.penalty_scores.pop(sla_str) + session.exec(select(Settings)).one().sla_penalty)
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


    # Returns a dict with all of the creds
    # Mostly used for debugging
    def get_all_creds(self) -> dict:
        with Session(db_engine) as session:
            data = session.exec(
                select(TeamCredsTable).where(
                    TeamCredsTable.team_id == self.identifier
                )
            ).all()
        credslist = dict()
        for creds in data:
            credslist.update({
                creds.name: json.loads(creds.creds)
            })
        return credslist

    # Adds a new credslist
    def add_creds(self, credslist: dict):
        with Session(db_engine) as session:
            session.add(
                TeamCredsTable(
                    name = credslist.items()[0].keys()[0],
                    team_id = self.identifier,
                    creds = credslist.items()[0].keys()[1]
                )
            )
            session.commit()

    # Returns a random user and password for use in service check
    # Parameter credlists is a list of names of the credlists to choose from
    def get_random_cred(self, credlists: list[str]) -> dict:
        with Session(db_engine) as session:
            chosen_list = json.loads(
                session.exec(
                    select(TeamCredsTable).where(
                        TeamCredsTable.name == random.choice(credlists)
                    ).where(
                        TeamCredsTable.team_id == self.identifier
                    )
                ).all()[0].creds
            )
        chosen = random.choice(list(chosen_list.items()))
        choice = {
            chosen[0]: chosen[1]
        }
        return choice

    # Performs a password change request
    # Parameter new_creds is a 2D dict, where the first key is the credlist name and the second is the user
    def pcr(self, new_creds: dict) -> None:
        with Session(db_engine) as session:
            for credlist, creds in new_creds.items():
                old_creds = session.exec(
                    select(TeamCredsTable).where(
                        TeamCredsTable.name == credlist
                    ).where(
                        TeamCredsTable.team_id == self.identifier
                    )
                ).one()
                mod_creds = json.loads(old_creds.creds)
                for user in creds.keys():
                    if user not in mod_creds:
                        continue
                    else:
                        mod_creds.update({
                            user: creds.get(user)
                        })
                old_creds.creds = json.dumps(mod_creds)
                session.commit()

    # Creates a new Team from the config info
    @classmethod
    def new(cls, services: list[str], data: dict):
        return cls(
            name=data['name'],
            identifier=data['identifier'],
            services=services,
            credlists=data['credlists']
        )

###################################################
# Class FileConfigLoader
# Locates all files and loads them into database
class FileConfigLoader():

    @classmethod
    def load_settings(cls):
        with open('./settings.toml', 'rb') as f:
            data = tomllib.load(f)
        with Session(db_engine) as session:
            session.add(
                Settings(
                    log_level=data['general']['log_level'],
                    competitor_info=data['general']['competitor_info'],
                    pcr_portal=data['general']['pcr_portal'],
                    inject_portal=data['general']['inject_portal'],
                    comp_name=data['general']['name'],
                    check_time=data['round']['check_time'],
                    check_jitter=data['round']['check_jitter'],
                    check_timeout=data['round']['check_timeout'],
                    check_points=data['round']['check_points'],
                    sla_requirement=data['round']['sla_requirement'],
                    sla_penalty=data['round']['sla_penalty'],
                    first_octets=data['environment']['first_octets'],
                    first_pod_third_octet=data['environment']['first_pod_third_octet']
                )
            )
            session.commit()

    @classmethod
    def load_boxes(cls):
        box_files = [f for f in listdir(boxes_path) 
                     if isfile(join(boxes_path, f)) 
                     and splitext(f)[-1].lower() == '.toml']
        for box_file in box_files:
            with open(join(boxes_path, box_file), 'rb') as f:
                data = tomllib.load(f)
                with Session(db_engine) as session:
                    session.add(
                        BoxTable(
                            name=splitext(box_file)[0].lower(),
                            identifier=data['identifier'],
                            config=tomli_w.dumps(data)
                        )
                    )
                    session.commit()
        

    @classmethod
    def load_creds(cls):
        cred_files = [f for f in listdir(creds_path) 
                     if isfile(join(creds_path, f)) 
                     and splitext(f)[-1].lower() == '.csv']
        for cred_file in cred_files:
             with open(join(creds_path, cred_file), 'r+') as f:
                data = csv.reader(f)
                creds = dict()
                for row in data:
                    creds.update({row[0]: row[1]})
                with Session(db_engine) as session:
                    session.add(
                        CredlistTable(
                            name=splitext(cred_file)[0].lower(),
                            creds=json.dumps(creds)
                        )
                    )
                    session.commit()

    @classmethod
    def load_injects(cls):
        inject_files = [f for f in listdir(injects_path) 
                       if isfile(join(injects_path, f)) 
                       and splitext(f)[-1].lower() == '.toml']
        for inject_file in inject_files:
            with open(join(injects_path, inject_file), 'rb') as f:
                data = tomllib.load(f)
                with Session(db_engine) as session:
                    session.add(
                        InjectTable(
                            num=int(splitext(inject_file)[0].lower()[-1]),
                            name=data['name'],
                            config=tomli_w.dumps(data)
                        )
                    )
                    session.commit()

    @classmethod
    def load_all(cls):
        cls.load_settings()
        cls.load_boxes()
        cls.load_creds()
        cls.load_injects()
