import time, sched, threading, queue
from os import listdir
from os.path import isfile, join, splitext
import random, csv
import logging

from enigma.models import Team, ScoreReport, TeamCreds, SLAReport, ScoreHistory, InjectReport
from enigma.util import Box, TeamManager, Inject, IPAddr
from enigma.database import db_session, del_db
from enigma.settings import boxes_path, creds_path, round_info, injects_path, comp_info, env_info

log = logging.getLogger(__name__)

# The main scoring engine for Enigma. Intended for use in production
# ScoringEngine is intended to continuously score services
class ScoringEngine():

    def __init__(self):
        
        self.delete_tables()

        # Initialize environment information
        self.name = comp_info.get('name')

        self.boxes = self.find_boxes()
        self.services = Box.full_service_list(self.boxes)
        self.credlists = self.find_credlists()
        self.teams = self.find_teams()
        self.managers = self.create_managers(
                self.teams, 
                self.services, 
                self.credlists
            )
        self.injects = ScoringEngine.find_injects()
        self.environment = IPAddr(env_info['first_octet'], env_info['second_octet'])

        # Verify settings
        if round_info['check_jitter'] >= round_info['check_delay']:
            log.critical('Check jitter cannot be larger than or equal to check delay, terminating...')
            raise SystemExit(0)
        if round_info['check_timeout'] >= round_info['check_delay'] - round_info['check_jitter']:
            log.critical('Check timeout must be less than delay - jitter, terminating...')
            raise SystemExit(0)

        # Starting from round 1
        self.round = 1

        self.check_scheduler = sched.scheduler(time.time, time.sleep)
        self.queue = queue.Queue()

    # Scoring loop methods
    def start_scoring(self):
        pass

    def stop_scoring(self):
        pass

    def pause_scoring(self):
        pass

    def scoring_worker(self):
        while True:
            item = self.queue.get()
            
    
    # Helper methods

    # Deletes all records except for team records
    def delete_tables(self):
        log.debug('deleting all data except for team data')
        db_session.query(ScoreReport).delete()
        db_session.query(TeamCreds).delete()
        db_session.query(SLAReport).delete()
        db_session.query(ScoreHistory).delete()
        db_session.query(InjectReport).delete()
        db_session.commit()
        db_session.close()

    # Find/create methods for relevant competition data

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
        teams = db_session.query(Team).all()
        db_session.close()
        if teams is None:
            log.critical('No teams were specified, terminating...')
            raise SystemExit(0)
        log.debug('teams found: {}'.format(teams))
        return teams
    
    @classmethod
    def create_teams(cls, starting_identifier: int, name_format: str, teams: list[int]):
        for team in teams:
            db_session.add(
                Team(
                    id = team,
                    username = name_format.format(team),
                    #pw_hash = pw,
                    identifier = starting_identifier + team - 1,
                    score = 0
                )
            )
            db_session.commit()

    @classmethod
    def find_injects(cls) -> list:
        log.debug('finding injects')
        inject_files = [f for f in listdir(injects_path) if isfile(join(injects_path, f)) and splitext(f)[-1].lower() == '.toml']
        if len(inject_files) == 0:
            log.warning('No injects were specified')
            return
        injects = list()
        for path in inject_files:
            injects.append(Inject.new(path))
        log.debug('injects found: {}'.format(injects))
        return injects







# A testing scoring engine. Is not meant for production
# TestScoringEngine is not intended to score services indefinitely, rather to test functionality of other modules within Enigma
class TestScoringEngine(ScoringEngine):
    
    def __init__(self):
        test_users = 10
        team_format = 'Team0{}'

        team_list = list()
        for i in range(1, test_users + 1):
            team_list.append(i)

        super().create_teams(1, team_format, team_list)

        super().__init__()
