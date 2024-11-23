import time
from os import listdir
from os.path import isfile, join, splitext
import random, csv, json
import logging

from concurrent.futures import as_completed, ThreadPoolExecutor
from multiprocessing import Process, Queue, get_logger

from enigma.models import Team, TeamCreds, SLAReport, ScoreHistory, InjectReport
from enigma.util import Box, TeamManager, Inject
from enigma.checks import Service
from enigma.database import db_session, del_db, init_db
from enigma.settings import boxes_path, creds_path, round_info, injects_path, comp_info, env_info, test_artifacts_path, scores_path

log = logging.getLogger('enigma')

# The main scoring engine for Enigma. Intended for use in production
# ScoringEngine is intended to continuously score services
class ScoringEngine():

    def __init__(self):
        
        log.info('++++==== Enigma Scoring Engine ====++++')
        log.info('Welcome to Enigma! Don\'t get puzzled!')

        log.debug('flushing non-team tables')
        self.delete_tables()

        log.info('Initializing environment information')
        # Initialize environment information
        self.name = comp_info.get('name')
        log.info('Competition name is {}'.format(self.name))

        self.boxes = self.find_boxes()
        log.info('All boxes have been sourced')

        self.services = Box.full_service_list(self.boxes)
        log.info('All services have been sourced')

        self.credlists = self.find_credlists()
        log.info('All creds have been sourced')

        self.teams = self.find_teams()
        log.debug('teams found, creating managers')

        self.managers = self.create_managers(
                self.teams, 
                self.services, 
                self.credlists
            )
        log.info('Teams have been identified')

        self.injects = ScoringEngine.find_injects()
        log.info('All injects have been sourced')

        self.environment = '{}.{}'.format(env_info['first_octet'], env_info['second_octet'])
        log.info('Network octets have been identified: {}'.format(self.environment))

        # Verify settings
        if round_info['check_jitter'] >= round_info['check_time']:
            log.critical('Check jitter cannot be larger than or equal to check delay, terminating...')
            raise SystemExit(0)
        log.debug('jitter has been checked')
        if round_info['check_timeout'] >= round_info['check_time'] - round_info['check_jitter']:
            log.critical('Check timeout must be less than delay - jitter, terminating...')
            raise SystemExit(0)
        log.debug('timeout has been checked')
        log.info('Round timing settings have been verified')
        log.info('Round time is {}, jitter is {}, and timeout is {}'.format(
            round_info['check_time'],
            round_info['check_jitter'],
            round_info['check_timeout']
        ))

        log.info('++++==== Environment Info Gathered ====++++')
        # Starting from round 1
        self.round = 1

    
    # Score check methods

    # Runs a full service score check for all teams, boxes, services
    # Assumes a 'presumed guilty' model for score checks.
    # A check can be assumed to be False unless proven True
    # This is important for the timeout to work!
    # Score checks are spawned in a separate process and are put on a timer
    # As score checks results come in, they are sent to the main thread if they are true (presumed guilty means no need to report guilt)
    # If all score checks do not finish before timeout, then the score check process will be forcibly terminated
    # Any results thus sent are the only passed score checks
    def score_services(self, round: int):
        log.info('++++==== Round {} ====++++'.format(round))
        log.info('Beginning scoring')
        log.debug('Setting up scoring functions and score check params')
        
        # identifies all service check functions and creates scoring params for each team

        # tired of keeping track of nested data structures
        # score_checks = dict['service': dict[]]
        # second dict = {'func': scoring function, 'check_data': list[check data]}
        score_checks = dict()
        for box in self.boxes:
            log.debug('working on Box {}'.format(box.name))
            for service in box.services:
                service_name = f'{box.name}.{service.name}'
                log.debug('working on Service {}'.format(service_name))
                score_check_info = {
                    'func': service.conduct_service_check
                }
                check_data = list()
                for team_id, team in self.managers.items():
                    log.debug('creating worker for {} for service {}'.format(team.id, service_name))
                    check_data.append(
                        self.setup_score_data(
                            service,
                            team,
                            box.identifier,
                            service_name
                        )
                    )
                score_check_info.update({
                    'check_data': check_data
                })
                score_checks.update({
                    service_name: score_check_info
                })

        # Creates a dict with presumed guilty check results
        # once again tired of data structures
        # reports = dict[team id: dict[service: result]]
        log.debug('creating presumed-guilty score reports')
        reports = dict()
        for service in self.services:
            for team_id in self.managers:
                if team_id not in reports:
                    reports.update({
                        team_id: {
                            service: False
                        }
                    })
                else:
                    reports[team_id].update({
                        service: False
                    })

        log.debug('starting score check process')
        results_queue = Queue()
        checks_process = Process(target=self.run_score_checks, args=(score_checks, results_queue))
        checks_process.start()
        checks_process.join(round_info['check_timeout'])

        if checks_process.is_alive():
            log.debug('checks timeout reached! terminating score check process immediately')
            checks_process.terminate()

        log.debug('updating innocent score checks')
        while not results_queue.empty():
            result = results_queue.get()
            reports[result[0]][result[1]] = True

        log.info('Tabulating all scores')
        for team_id, team in self.managers.items():
            team.tabulate_scores(round, reports[team_id])

        log.info('Score checks for round {} complete.'.format(round))

    # Runs all score checks. Each score check is handled in a thread
    # Pushes all positive score checks to the queue
    def run_score_checks(self, check_data: dict, results_queue: Queue):
        log = get_logger()
        log.debug('score check worker spawned, starting score checks')
        threads = len(self.managers.keys()) * len(self.services)

        executor = ThreadPoolExecutor(max_workers = threads)
        results = list()
        for service, info in check_data.items():
            for info_morsel in info['check_data']:
                results.append(
                    executor.submit(
                        info['func'],
                        info_morsel
                    )
                )
        log.debug('all score check workers spawned')
        for result in as_completed(results):
            if result.result() is not None:
                results_queue.put(result.result())
        log.debug('all score checks finished before timeout')
        executor.shutdown()

    # Creates a tuple of data important to scoring
    def setup_score_data(self, service: Service, team: TeamManager, identifier: int, service_name: str):
        log.debug('creating score params data')
        data = dict()
        data.update({
            'addr': '{}.{}.{}'.format(
                self.environment,
                team.id,
                identifier
            )
        })
        data.update({
            'team': team.id,
            'service': service_name
        })
        if hasattr(service, 'credlist'):
            log.debug('credlist requirement found, grabbing random cred')
            data.update({
                'creds': team.get_random_cred(service.credlist)
            })
        log.debug('score params set')
        return data

    def export_all_as_csv(self):
        for team_id, team in self.managers.items():
            team.scores.export_csv('{}_scores'.format(
                db_session.query(Team).filter(Team.id == team_id).one().username
            ), scores_path)
            db_session.close()

    # Deletes all records except for team records
    def delete_tables(self):
        log.debug('deleting all data except for team data')
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
    
    def __init__(self, test_users: int, user_fmt: str):

        log.info('++++==== Testing Engine ====++++')
        log.info('Flushing tables and reiniting')
        del_db()
        init_db()

        log.info('Creating new teams')
        team_list = list()
        for i in range(1, test_users + 1):
            team_list.append(i)

        super().create_teams(1, user_fmt, team_list)

        log.info('Calling base ScoreEngine init')
        super().__init__()
