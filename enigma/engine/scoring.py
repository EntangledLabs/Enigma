import time, sched
import random, json

from multiprocessing import Process, Queue

from sqlmodel import Session, select, delete

from engine.scoreutil import run_score_checks
from engine.util import Box, Inject, Team, Credlist, FileConfigLoader
from engine.database import db_engine, init_db, del_db
from engine.models import TeamTable, CredlistTable, TeamCredsTable, SLAReport, InjectReport, ScoreReport, InjectTable, BoxTable
from engine.settings import settings, scores_path

class ScoringEngine():
    
    def __init__(self):
        self.delete_tables()

        FileConfigLoader.load_all()

        # Initialize environment information
        self.name = settings['general']['name']
        self.boxes = self.find_boxes()
        self.services = Box.full_service_list(self.boxes)

        self.credlists = self.find_credlists()

        self.teams = self.find_teams()

        self.environment = settings['environment']['first_octets']

        # Verify settings
        if settings['round']['check_jitter'] >= settings['round']['check_time']:
            raise SystemExit(0)
        if settings['round']['check_timeout'] >= settings['round']['check_time'] - settings['round']['check_jitter']:
            raise SystemExit(0)

        # Starting from round 1
        self.round = 1

        # Setting pause and commands queue
        self.pause = False

    async def run(self, total_rounds: int=0):
        print('horray u didnt done goof it up')
        while self.round <= total_rounds or total_rounds == 0:
            while self.pause:
                time.sleep(0.1)
            self.score_services(self.round)
            self.round = self.round + 1
            wait_time = settings['round']['check_time'] + random.randint(-settings['round']['check_jitter'], settings['round']['check_jitter']) 
            time.sleep(wait_time)
        self.export_all_as_csv()

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
        # identifies all service check functions and creates scoring params for each team

        # tired of keeping track of nested data structures
        # score_checks = dict['service': dict[]]
        # second dict = {'func': scoring function, 'check_data': list[check data]}
        score_checks = dict()
        for box in self.boxes:
            for service in box.services:
                service_name = f'{box.name}.{service.name}'
                score_check_info = {
                    'func': service.conduct_service_check
                }
                check_data = list()
                for team_id, team in self.teams.items():
                    check_data.append(
                        self.setup_check_data(
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
        reports = dict()
        all_services = Box.full_service_list(self.boxes)
        for service in all_services:
            for team_id in self.teams:
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

        results_queue = Queue()
        checks_process = Process(target=run_score_checks, args=(score_checks, results_queue, self.teams, all_services))
        checks_process.start()
        checks_process.join(settings['round']['check_timeout'])

        if checks_process.is_alive():
            checks_process.kill()

        while not results_queue.empty():
            result = results_queue.get()
            reports[result[0]][result[1]] = True

        for team_id, team in self.teams.items():
            team.tabulate_scores(round, reports[team_id])

    # Deletes all records except for team records
    def delete_tables(self):
        with Session(db_engine) as session:
            session.exec(delete(TeamCredsTable))
            session.exec(delete(SLAReport))
            session.exec(delete(ScoreReport))
            session.exec(delete(InjectReport))
            session.exec(delete(InjectTable))
            session.exec(delete(CredlistTable))
            session.exec(delete(BoxTable))
            session.commit()

    # Find/create methods for relevant competition data

    def export_all_as_csv(self):
        for team_id, team in self.teams.items():
            team.export_csv('{}_scores'.format(team.name), scores_path)

    def find_boxes(self):
        boxes = list()
        with Session(db_engine) as session:
            db_boxes = session.exec(select(BoxTable)).all()
            for db_box in db_boxes:
                boxes.append(
                    Box.new(db_box.config)
                )
        return boxes

    def find_credlists(self):
        credlists = list()
        with Session(db_engine) as session:
            db_credlists = session.exec(select(CredlistTable)).all()
        for db_credlist in db_credlists:
            credlists.append(
                Credlist.new({
                    'name': db_credlist.name,
                    'creds': json.loads(db_credlist.creds)
                })
            )
        return credlists

    def find_teams(self):
        teams = dict()
        with Session(db_engine) as session:
            db_teams = session.exec(select(TeamTable)).all()
        for db_team in db_teams:
            teams.update({
                db_team.identifier: Team.new(
                    self.services,
                    {
                        'name': db_team.name,
                        'identifier': db_team.identifier,
                        'credlists': self.credlists
                    }
                )
            })
        return teams

    def find_injects(self):
        injects = list()
        with Session(db_engine) as session:
            db_injects = session.exec(select(InjectTable)).all()
        for db_inject in db_injects:
            injects.append(
                Inject.new(data=db_inject.config)
            )
        return injects
    
class TestScoringEngine(ScoringEngine):
    
    def __init__(self, test_users: int, user_fmt: str):
        team_list = list()
        for i in range(1, test_users + 1):
            team_list.append(i)

        with Session(db_engine) as session:
            for team in team_list:
                session.add(
                TeamTable(
                    name=user_fmt.format(team),
                    identifier=team,
                    score=0
                )
            )

        super().__init__()