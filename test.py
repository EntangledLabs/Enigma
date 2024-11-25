from enigma.scoring import TestScoringEngine
from multiprocessing import Process, Queue, current_process
import time

if __name__ == '__main__':
    engine = TestScoringEngine(5, 'Team0{}')
    engine.run(1)
    engine.export_all_as_csv()