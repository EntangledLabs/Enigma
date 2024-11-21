import time, uuid
from os import listdir
from os.path import isfile, join, splitext
import random, csv
import logging

from enigma.models import Team, TeamCreds
from enigma.util import Box, ScoreBreakdown, TeamManager
from enigma.database import db_session
from enigma.settings import boxes_path, creds_path, possible_services, round_info

log = logging.getLogger(__name__)

class ScoringEngine():

    def __init__(self):
        
        # Initialize environment information
        self.boxes = self.find_boxes()
        self.credlists = self.find_credlists()
        self.managers = ScoringEngine.create_managers(
                ScoringEngine.find_teams(), 
                Box.full_service_list(ScoringEngine.find_boxes()), 
                ScoringEngine.find_credlists()
            )

        # Verify settings
        if round_info['check_jitter'] >= round_info['check_delay']:
            log.critical('Check jitter cannot be larger than or equal to check delay, terminating...')
            raise SystemExit(0)
        if round_info['check_timeout'] >= round_info['check_delay'] - round_info['check_jitter']:
            log.critical('Check timeout must be less than delay - jitter, terminating...')
            raise SystemExit(0)

        # Starting from round 1
        self.round = 1

    def start_scoring(self):
        pass

    def stop_scoring(self):
        pass

    def pause_scoring(self):
        pass

    @classmethod
    def create_managers(cls, teams: list, services:list, credlists: dict) -> dict:
        log.debug('creating managers')
        managers = dict()
        for team in teams:
            managers.update({
                team.id: TeamManager.new(
                    team.id,
                    services,
                    credlists
                )
            })
        return managers

    @classmethod
    def find_credlists(cls) -> dict:
        log.debug('finding credlists')
        cred_files = [f for f in listdir(creds_path) if isfile(join(creds_path, f)) and splitext(f)[-1].lower() == '.csv']
        if len(cred_files) == 0:
            log.critical('No credlists were specified, terminating...')
            raise SystemExit(0)
        credlists = dict()

        for path in cred_files:
            with open(join(creds_path, path), 'r+') as f:
                data = csv.reader(f)
                creds = dict()
                for row in data:
                    creds.update({row[0]: row[1]})
                credlists.update({
                    splitext(path)[0].lower(): creds
                })
        log.debug('credlists found: {}'.format(credlists))
        return credlists

    @classmethod
    def find_boxes(cls) -> list:
        log.debug('finding boxes')
        box_files = [f for f in listdir(boxes_path) if isfile(join(boxes_path, f)) and splitext(f)[-1].lower() == '.toml']
        if len(box_files) == 0:
            log.critical('No boxes were specified, terminating...')
            raise SystemExit(0)
        boxes = list()
        for path in box_files:
            boxes.append(Box.new(path))
        log.debug('boxes found: {}'.format(boxes))
        return boxes
    
    @classmethod
    def find_teams(cls) -> list:
        log.debug('finding teams')
        teams = db_session.query(Team).filter(Team.id != 0).all()
        db_session.close()
        if teams is None:
            log.critical('No teams were specified, terminating...')
            raise SystemExit(0)
        log.debug('teams found: {}'.format(teams))
        return teams
    
    @classmethod
    def find_injects(cls) -> list:
        log.debug('finding injects')