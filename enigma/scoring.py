import time, uuid
from os import listdir
from os.path import isfile, join, splitext
import random, pickle

from enigma.models import User, CredListDB
from enigma.util import Box, CredList, ScoreBreakdown, possible_services
from enigma.database import db_session
from enigma.settings import boxes_path, creds_path

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