import random
import time
from os.path import join
from sys import executable as interpreter
import subprocess
import threading

from enigma.checks import Service

from enigma.enigma_logger import log
from enigma.engine import static_path, checks_path
from enigma.broker import RabbitMQ

from enigma.models.box import Box
from enigma.models.credlist import Credlist
from enigma.models.team import RvBTeam
from enigma.models.settings import Settings

class ScoringEngine:

    def __init__(self):
        log.info("Initializing scoring engine")
        # Setting flags
        self.pause = False
        self.stop = False
        self.teams_detected = False
        self.engine_lock = False
        log.info("Scoring engine run flags set")

class RvBScoringEngine(ScoringEngine):

    def __init__(self):
        super().__init__()

        log.info("Searching for RvB competition configurations")
        self.boxes = Box.find_all()
        self.credlists = Credlist.find_all()
        self.services = Box.all_service_names(self.boxes)
        log.info("RvB competition environment loaded")

        log.info("Searching for RvB teams")
        self.teams = RvBTeam.find_all(self.services)
        log.info("RvB teams found, creating team credlists")
        for team in self.teams:
            team.create_credlists(
                self.credlists
            )
        log.info("RvB teams loaded")

        self.round = 1

        log.info("RvB scoring engine ready...")

    # Starts the scoring engine loop
    def run(self, total_rounds: int = 0):
        # Initializing run
        log.info('Starting scoring!')
        self.engine_lock = True

        # Main loop
        while (self.round <= total_rounds or total_rounds == 0) and not self.stop:
            # Checking for pause
            log.info(f'++== Round {self.round} ==++')
            if self.pause:
                log.info('Pausing scoring!')
                while self.pause:
                    time.sleep(0.1)
                log.info('Resuming scoring...')

            # Updating boxes and services
            log.info('Retrieving up-to-date environment information')
            self.boxes = Box.find_all()
            self.services = Box.all_service_names(self.boxes)

            # Run score checks
            log.info('Running score checks')
            self.score_services()

            log.info(f'Round {self.round} scoring complete! Waiting for next round start...')

            if self.round == total_rounds or self.stop:
                break

            wait_jitter = random.randint(
                -Settings.get_setting('check_jitter'),
                Settings.get_setting('check_jitter')
            )
            wait_time = Settings.get_setting('check_time') + wait_jitter
            log.debug(f'Wait jitter: {wait_jitter} seconds')
            log.debug(f'Wait time: {wait_time} seconds')

            time.sleep(wait_time)

            # Advancing round counter
            self.round = self.round + 1

        # Finishing up scoring
        log.info('Stopping scoring!')
        self.stop = False
        self.pause = False
        self.engine_lock = False

        # Exporting end-of-scoring data
        log.info('Exporting individual team score breakdowns')
        for team in self.teams:
            team.export_breakdowns(f'team{team.identifier}_final', static_path)

    # Score check methods

    # Runs a full service score check for all teams, boxes, services
    # Assumes a 'presumed guilty' model for score checks.
    # A check can be assumed to be False unless proven True
    # This is important for the timeout to work!
    # Score checks are spawned in a separate process and are put on a timer
    # As score checks results come in, they are sent to the main thread if they are true (presumed guilty means no need to report guilt)
    # If all score checks do not finish before timeout, then the score check process will be forcibly terminated
    # Any results thus sent are the only passed score checks
    def score_services(self):
        log.debug('Starting scoring services')
        # Creating a dict full of score checks
        # score_checks = {service name: {'func': scoring function, 'check_data': [all check data]}}
        score_checks = []
        first_octets = Settings.get_setting('first_octets')
        for box in self.boxes:
            for service in box.services:
                for team in self.teams:
                    # Default check options
                    check_data = [
                        f'{box.name}.{service.name}',
                        f'{first_octets}.{team.identifier}.{box.identifier}'
                    ]

                    # Additional check options
                    check_data.extend(
                        self.get_check_options(
                            service,
                            team
                        )
                    )

                    # Add to all score check data
                    score_checks.append(
                        check_data
                    )

        log.debug('Created score checks with check data')

        # Presumed guilty check results
        # reports = {team identifier: {service: [result, msg]}}
        reports = {}
        for team in self.teams:
            team_results = {}
            for service in self.services:
                team_results[service] = [False, 'Timed out']
            reports[team.identifier] = team_results
        log.debug('Created presumed guilty check results')

        # run score checks
        results = self.run_score_checks(score_checks)
        log.debug('Finished score checks, proceeding to update scores')

        # Update results with proven innocent check results
        for result in results:
            reports[result[0]][result[1]][0] = True
            reports[result[0]][result[1]][1] = result[2]
        log.debug('Scores updated, proceeding to tabulate scores')

        # Tabulate scores for each team
        for team in self.teams:
            team.tabulate_scores(self.round, reports[team.identifier])

        log.debug('Finished scoring services')

    # Finds and applies check options for a service
    def get_check_options(self, service: Service, team: RvBTeam):
        log.debug(f'Creating check data for team {team.identifier} with service {service.name}')
        check_options = []

        # If check requires a credlist, get a random cred and add it to options
        if hasattr(service, 'credlist'):
            check_options.extend([
                '--creds',
                str(team.get_random_cred(service.credlist))
            ])

        # If check has a port, add to options
        if hasattr(service, 'port'):
            check_options.extend([
                '--port',
                str(service.port)
            ])

        # If check has auth methods, add to options
        if hasattr(service, 'auth'):
            check_options.extend([
                '--auth',
                str(service.auth)
            ])

        # If check has key file, add path to options
        if hasattr(service, 'keyfile'):
            check_options.extend([
                '--keyfile',
                str(service.keyfile)
            ])

        # If check has a specific path to check, add path to options
        if hasattr(service, 'path'):
            check_options.extend([
                '--path',
                str(service.path)
            ])

        return check_options

    # Run score checks
    def run_score_checks(self, check_options: list[list]) -> list[tuple]:
        log.debug('Running scoring checks')
        check_timeout = Settings.get_setting('check_timeout')

        # First part of the subprocess.Popen args, with the python interpreter and the path of the run_check.py script
        run_check = [
            interpreter,
            join(checks_path, 'run_check.py')
        ]

        # Custom check thread class that encapsulates a subprocess.Popen object
        class CheckThread:
            def __init__(self, args: list):
                self.args = args
                self.process = None

            def run(self):
                def target():
                    self.process = subprocess.Popen(self.args)
                thread = threading.Thread(target=target)
                thread.start()

            def kill(self):
                self.process.kill()

        # Creates CheckThreads for each service and runs
        threads = []
        for check_option in check_options:

            args = run_check + check_option
            thread = CheckThread(args)
            threads.append(thread)
            thread.run()

        # Attaching to RabbitMQ queue for 'enigma.engine.results' and adding each results to returned list
        results = []
        timeout = time.time() + check_timeout
        with RabbitMQ() as rabbit:
            result = rabbit.channel.queue_declare('', exclusive=True)
            rabbit.channel.queue_bind(
                exchange='enigma',
                queue=result.method.queue,
                routing_key='enigma.engine.results'
            )

            while time.time() <= timeout:
                method_frame, header_frame, body = rabbit.channel.basic_get(queue=result.method.queue, auto_ack=True)
                if body != None:
                    check_result = body.decode('utf-8')
                    check_result = check_result.split('|')
                    check_result[0] = int(check_result[0])
                    results.append(check_result)

        # After timeout, kill each process
        for thread in threads:
            thread.kill()
        print(results)
        return results