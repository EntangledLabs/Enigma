from multiprocessing import Queue
from concurrent.futures import ThreadPoolExecutor, as_completed

from engine.util import Team

# Runs all score checks. Each score check is handled in a thread
# Pushes all positive score checks to the queue
def run_score_checks(check_data: dict, results_queue: Queue, teams: dict[Team], services: list[str]):
    threads = len(teams.keys()) * len(services)
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
    for result in as_completed(results):
        if result.result() is not None:
            results_queue.put(result.result())
    executor.shutdown()