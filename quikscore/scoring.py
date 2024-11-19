import time, tomllib, random, csv, uuid
from os import listdir
from os.path import isfile, join, splitext
from enum import Enum
import random, pickle

from quikscore.models import ScoreReport, User, CredListDB
from quikscore.database import db_session
from quikscore.checks import *

boxes_path = './boxes/'
creds_path = './creds/'
possible_services = Service.__subclasses__()

class ScoringEngine():

    def __init__(self, check_delay: int, check_jitter: int, check_timeout: int, check_points: int, sla_req: int, sla_penalty: int):
        
        self.boxes = self.find_boxes()
        self.teams = self.find_teams()

        self.create_credlists()

        if check_jitter >= check_delay:
            raise ValueError(
                'Check jitter cannot be larger than or equal to check delay'
            )
        if check_timeout >= check_delay - check_jitter:
            raise ValueError(
                'Check timeout must be less than delay - jitter'
            )
        
        self.check_delay = check_delay
        self.check_jitter = check_jitter
        self.check_timeout = check_timeout
        self.check_points = check_points
        self.sla_req = sla_req
        self.sla_penalty = sla_penalty

    def start_scoring(self):
        pass

    def stop_scoring(self):
        pass

    def pause_scoring(self):
        pass

    def create_credlists(self):
        cred_files = [f for f in listdir(creds_path) if isfile(join(creds_path, f)) and splitext(f)[-1].lower() == '.csv']
        if len(cred_files) == 0:
            raise RuntimeError(
                'No credlists found!'
            )
        credlists = list()
        for path in cred_files:
            credlists.append(CredList.new(path))
        
        for team in self.teams:
            for credlist in credlists:
                db_session.add(
                    CredListDB(
                        id = uuid.uuid4(),
                        team_id = team.id,
                        name = credlist.name,
                        creds = pickle.dumps(credlist)
                    )
                )
                db_session.commit()
                db_session.close()

    @classmethod
    def find_boxes(cls) -> list:
        box_files = [f for f in listdir(boxes_path) if isfile(join(boxes_path, f)) and splitext(f)[-1].lower() == '.toml']
        if len(box_files) == 0:
            raise RuntimeError(
                'No boxes found!'
            )
        boxes = list()
        for path in box_files:
            boxes.append(Box.new(path))

        return boxes
    
    @classmethod
    def find_teams(cls) -> list:
        teams = db_session.query(User).all()
        db_session.close()
        if teams is None:
            raise RuntimeError(
                'No teams were found!'
            )
        return teams

class Box():

    def __init__(self, name: str, identifier: int, services: list):
        self.name = name
        self.identifier = identifier
        self.services = services
    
    def __repr__(self):
        return '<{}> named \'{}\' with services {}'.format(type(self).__name__, self.name, self.services)

    @classmethod
    def compile_services(cls, data: dict):
        services = list()
        for service in possible_services:
            if service.name in data:
                services.append(service.new(data[service.name]))
        return services

    @classmethod
    def new(cls, path: str):
        with open(join(boxes_path, path), 'rb') as f:
            data = tomllib.load(f)
        try:
            box = cls(
                splitext(path)[0].lower(), 
                data['identifier'],
                cls.compile_services(data),
                )
        except:
            raise RuntimeError(
                '{} is not configured correctly'.format(path)
            )
        return box
    
class CredList():

    def __init__(self, name: str, creds: dict):
        self.name = name
        self.creds = creds

    def get_random_user(self):
        chosen = random.choice([self.creds.keys()])
        return {
            chosen: self.creds[chosen]
        }
    
    def get_random_user_addon(self, addon: dict):
        both = list()
        both.extend(self.creds.keys())
        both.extend(addon.keys())
        chosen = random.choice(both)
        if chosen in self.creds.keys():
            return {
                chosen: self.creds[chosen]
            }
        else:
            return {
                chosen: addon[chosen]
            }
    
    def pcr(self, updated_creds: dict):
        self.creds.update(updated_creds)

    def __repr__(self):
        return '<{}> with name {} and {} creds'.format(type(self).__name__, self.name, len(self.creds.keys()))

    @classmethod
    def new(cls, path: str):
        with open(join(creds_path, path), 'r+') as f:
            data = csv.reader(f)
            creds = dict()
            for row in data:
                creds.update({row[0]: row[1]})
        return cls(splitext(path)[0].lower(), creds)