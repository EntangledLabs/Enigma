import random, json
import asyncio
from os.path import join

from sqlmodel import Session, select, delete

from engine.util import Box, Inject, Team, Credlist
from engine.auth import ParableUserTable, get_hash
from engine.database import db_engine
from engine.models import *
from engine.checks import Service
from engine import log, static_path

class ScoringEngine():
    
    def __init__(self):
        # Setting flags
        self.pause = False
        self.stop = False
        self.teams_detected = False
        self.enginelock = False

        # Initialize environment information
        with Session(db_engine) as session:
            self.check_time = session.exec(select(Settings)).one().check_time
            self.check_jitter = session.exec(select(Settings)).one().check_jitter
            self.check_timeout = session.exec(select(Settings)).one().check_timeout
            self.check_points = session.exec(select(Settings)).one().check_points

            self.sla_requirement = session.exec(select(Settings)).one().sla_requirement
            self.sla_penalty = session.exec(select(Settings)).one().sla_penalty

            self.environment = session.exec(select(Settings)).one().first_octets
        
        self.find_boxes()
        self.services = Box.full_service_list(self.boxes)
        self.find_credlists()
        self.find_teams()
        self.find_injects()

        try:
            with Session(db_engine) as session:
                session.add(
                    ParableUserTable(
                        username='admin',
                        identifier=0,
                        permission_level=0,
                        pwhash=get_hash('enigma')
                    )
                )
                session.add(
                    ParableUserTable(
                        username='green',
                        identifier=-1,
                        permission_level=1,
                        pwhash=get_hash('parable')
                    )
                )
                session.commit()
        except:
            pass

        # Verify settings
        if self.check_jitter >= self.check_time:
            raise SystemExit(0)
        if self.check_timeout >= self.check_time - self.check_jitter:
            raise SystemExit(0)

        # Starting from round 1
        self.round = 1

    async def run(self, total_rounds: int=0):
        self.enginelock = True
        with Session(db_engine) as session:
            self.name = session.exec(select(Settings)).one().comp_name

        self.print_comp_info()

        log.info(f'++== {self.name} ==++')
        while (self.round <= total_rounds or total_rounds == 0) and not self.stop:
            log.info('Round {}'.format(self.round))

            if self.pause:
                log.info('Pausing scoring')
            while self.pause:
                await asyncio.sleep(0.1)

            log.info('Starting scoring')

            self.find_boxes()
            self.services = Box.full_service_list(self.boxes)
            self.find_injects()

            await asyncio.wait(
                [asyncio.create_task(
                    self.score_services(self.round)
                )],
                return_when=asyncio.ALL_COMPLETED
            )

            log.info('Round {} done! Waiting for next round start...'.format(self.round))

            wait_time = self.check_time + random.randint(-self.check_jitter, self.check_jitter)
            self.export_all_as_csv('{}' + f'_{self.round}_scores')
            await asyncio.sleep(wait_time)
            self.round = self.round + 1

        log.info('Stopping scoring!')

        self.stop = False
        self.enginelock = False

        log.info('Exporting CSVs with competitor data')
        self.export_all_as_csv('{}_final_scores')

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
        print(f'#1 score services called round {round}')
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

        print(f'#2 making presumed guilty check results round {round}')
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

        print(f'#3 running score checks round {round}')
        finished, pending = await asyncio.wait([
                asyncio.create_task(
                    self.run_score_checks(score_checks, self.teams, self.services)
                )
            ],
            return_when=asyncio.ALL_COMPLETED
        )

        print(len(finished))
        print(finished)

        results = finished.pop().result()

        print(results)

        print(f'#4 writing reports round {round}')
        for result in results:
            reports[result[0]][result[1]] = True

        for team_id, team in self.teams.items():
            print(team)
            team.tabulate_scores(round, reports[team_id])

        print(f'#5 done scoring services round {round}')
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
    
    # Aync method to run score checks, allowing Enigma to focus on fulfilling API requests in the meantime
    async def run_score_checks(self, check_data: dict, teams: dict[Team], services: list[str]):
        results = []
        tasks = []
        for service, info in check_data.items():
            for info_morsel in info['check_data']:
                tasks.append(asyncio.create_task(info['func'](info_morsel)))

        try:
            async for result in asyncio.as_completed(tasks, timeout=self.check_timeout):
                data = result.result()
                if data is not None:
                    results.append(data)
        except TimeoutError:
            for task in tasks:
                if not task.done():
                    task.cancel()
        
        return results
    
    def reset_scores(self):
        with Session(db_engine) as session:
            teams = session.exec(select(TeamTable)).all()
            for team in teams:
                team.score = 0
                session.add(team)
                session.commit()
        self.find_teams()

    # Find/create methods for relevant competition data

    def export_all_as_csv(self, fmt: str):
        for team_id, team in self.teams.items():
            team.export_scores_csv(fmt.format(team.name), static_path)

    def find_boxes(self):
        boxes = list()
        with Session(db_engine) as session:
            db_boxes = session.exec(select(BoxTable)).all()
            for db_box in db_boxes:
                boxes.append(
                    Box.new(db_box.name, db_box.config)
                )
        self.boxes = boxes

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
        self.credlists = credlists

    def find_teams(self):
        teams = dict()
        with Session(db_engine) as session:
            session.exec(delete(TeamCredsTable))
            session.commit()
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
        self.teams_detected = True if len(teams) != 0 else False
        self.teams = teams

    def find_injects(self) -> list[Inject]:
        injects = list()
        with Session(db_engine) as session:
            db_injects = session.exec(select(InjectTable)).all()
        for db_inject in db_injects:
            injects.append(
                Inject.new(db_inject.num, db_inject.config)
            )
        self.injects = injects

    # Creates a human-readable version of the entire competition configuration
    def print_comp_info(self):
        filename = f'{self.name}_enigma_info.txt'
        with open(join(static_path, filename), 'w+') as f:
            with Session(db_engine) as session:
                settings = session.exec(select(Settings)).one()
            f.writelines([
                '++++==== Enigma Scoring Engine Configuration ====++++\n',
                f'Competition name: {settings.comp_name}\n\n'
            ])

            f.writelines([
                '++++==== Competition Settings ====++++\n',
                f'Competitor information level: {settings.competitor_info}\n',
                f'PCR portal active: {settings.pcr_portal}\n',
                f'Inject portal active: {settings.inject_portal}\n\n',
                f'Time between service checks: {settings.check_time} seconds\n',
                f'Check jitter: {settings.check_jitter} seconds\n',
                f'Service check timeout: {settings.check_timeout} seconds\n\n',
                f'Points awarded per successful service check: {settings.check_points} points\n',
                f'Number of checks failed to incur SLA: {settings.sla_requirement} checks\n',
                f'Points deducted per SLA violation: {settings.sla_penalty} points\n\n',
                f'Pod network octets: {settings.first_octets}\n',
                f'First pod identifying octet: {settings.first_pod_third_octet}\n\n'
            ])

            for box in self.boxes:
                f.writelines([
                    '++++==== Box Info ====++++\n',
                    f'Box name: {box.name}\n',
                    f'Box identifying octet: {box.identifier}\n\n'
                ])
                for service in box.services:
                    f.writelines([
                        '---- Service Info ----\n',
                        f'Service type: {service.name}\n'
                    ])
                    if hasattr(service, 'port'):
                        f.write(
                            f'Port: {service.port}\n'
                        )
                    if hasattr(service, 'auth'):
                        f.write(
                            f'Auth types: {', '.join(auth for auth in service.auth)}\n'
                        )
                    if hasattr(service, 'keyfile'):
                        f.write(
                            f'Keyfile: {service.keyfile}\n'
                        )
                    if hasattr(service, 'path'):
                        f.write(
                            f'Check path: {service.path}\n'
                        )
                f.write('\n')

            for credlist in self.credlists:
                f.writelines([
                    '++++==== Credlist Info ====++++\n',
                    f'Credlist name: {credlist.name}\n\n'
                ])
                for user, password in credlist.creds.items():
                    f.write(
                        f'{user}: {password}\n'
                    )
                f.write('\n')

            for inject in self.injects:
                f.writelines([
                    '++++==== Inject Info ====++++\n',
                    f'Inject name: {inject.name}\n',
                    f'Inject number: {inject.id}\n'
                ])


  
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