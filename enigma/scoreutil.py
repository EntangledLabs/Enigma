from multiprocessing import Queue, Process, get_logger, current_process
from concurrent.futures import ThreadPoolExecutor, as_completed

from enigma.util import Box, TeamManager
from enigma.checks import Service
from enigma.settings import round_info, scores_path
from enigma.database import db_session
from enigma.models import Team

# Runs all score checks. Each score check is handled in a thread
# Pushes all positive score checks to the queue
def run_score_checks(check_data: dict, results_queue: Queue, managers: dict[TeamManager], services: list[str]):
    log = get_logger()
    log.debug('score check worker spawned, starting score checks')
    threads = len(managers.keys()) * len(services)

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