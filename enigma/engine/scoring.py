import time, sched
import random, json
import asyncio

from multiprocessing import Process, Queue

from sqlmodel import Session, select, delete

from engine.util import Box, Inject, Team, Credlist, FileConfigLoader
from engine.database import db_engine, init_db, del_db
from engine.models import TeamTable, CredlistTable, TeamCredsTable, SLAReport, InjectReport, ScoreReport, InjectTable, BoxTable, Settings
from engine.settings import scores_path
from engine.checks import Service
from engine import log

class ScoringEngine():
    
    def __init__(self):
        self.delete_tables()

        FileConfigLoader.load_all()

        # Initialize environment information
        with Session(db_engine) as session:
            self.name = session.exec(select(Settings)).one().comp_name
            self.boxes = self.find_boxes()
            self.services = Box.full_service_list(self.boxes)

            self.credlists = self.find_credlists()

            self.teams = self.find_teams()

            self.environment = session.exec(select(Settings)).one().first_octets

            # Verify settings
            if session.exec(select(Settings)).one().check_jitter >= session.exec(select(Settings)).one().check_time:
                raise SystemExit(0)
            if session.exec(select(Settings)).one().check_timeout >= session.exec(select(Settings)).one().check_time - session.exec(select(Settings)).one().check_jitter:
                raise SystemExit(0)

        # Starting from round 1
        self.round = 1

        # Setting pause and commands queue
        self.pause = False

    async def run(self, total_rounds: int=0):
        print('horray u didnt done goof it up')
        while self.round <= total_rounds or total_rounds == 0:
            print('round {}'.format(self.round))
            while self.pause:
                await asyncio.sleep(0.1)
            await self.score_services(self.round)
            self.round = self.round + 1
            with Session(db_engine) as session:
                check_jitter = session.exec(select(Settings)).one().check_jitter
                wait_time = session.exec(select(Settings)).one().check_time + random.randint(-check_jitter, check_jitter) 
            print('round 1 done')
            await asyncio.sleep(wait_time)
        print('all done!')
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
    async def score_services(self, round: int):
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

        results = await self.run_score_checks(score_checks, self.teams, self.services)
        
        for result in results:
            reports[result[0]][result[1]] = True

        for team_id, team in self.teams.items():
            team.tabulate_scores(round, reports[team_id])

    # Creates a dict of data important to scoring
    # each check data consists of the following:
    # {
    #   'addr': ip address of team's box,
    #   'team': team number,
    #   'service': service being scored,
    #   'creds': if creds are specified as a requirement, then a random cred
    # }
    def setup_check_data(self, service: Service, team: Team, box_ident: int, service_name: str):
        data = dict()
        data.update({
            'addr': '{}.{}.{}'.format(
                self.environment,
                team.identifier,
                box_ident
            )
        })
        data.update({
            'team': team.identifier,
            'service': service_name
        })
        if hasattr(service, 'credlist'):
            data.update({
                'creds': team.get_random_cred(service.credlist)
            })
        return data
    
    async def run_score_checks(self, check_data: dict, teams: dict[Team], services: list[str]):
        results = []
        tasks = []
        for service, info in check_data.items():
            for info_morsel in info['check_data']:
                tasks.append(asyncio.create_task(info['func'](info_morsel)))

        try:
            with Session(db_engine) as session:
                async for result in asyncio.as_completed(tasks, timeout=session.exec(select(Settings)).one().check_timeout):
                    data = result.result()
                    if data is not None:
                        results.append(data)

        except TimeoutError:
            for task in tasks:
                if not task.done():
                    task.cancel()
        
        return results
    
    async def score_check_task(self):
        pass

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
            team.export_scores_csv('{}_scores'.format(team.name), scores_path)

    def find_boxes(self):
        boxes = list()
        with Session(db_engine) as session:
            db_boxes = session.exec(select(BoxTable)).all()
            for db_box in db_boxes:
                boxes.append(
                    Box.new(db_box.name, db_box.config)
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
                Inject.new(db_inject.num, db_inject.config)
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
            session.commit()

        super().__init__()