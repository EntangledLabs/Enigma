import tomllib, csv, json, random
import pkgutil, inspect
import os, hashlib
from enigma.models import Team, TeamCreds, SLAReport, ScoreHistory, InjectReport
from enigma.database import db_session, init_db, del_db
from enigma.checks import Service, SSHService, HTTPService, HTTPSService
from enigma.scoring import ScoringEngine, TestScoringEngine
from enigma.util import ScoreBreakdown, TeamManager, Box, Inject
from enigma.settings import logs_path, injects_path, test_artifacts_path
import logging

from datetime import datetime

import threading, time, queue
import concurrent.futures

from os import listdir
from os.path import isfile, join, splitext

"""def test_scoring(team: int):
    time.sleep(random.randint(1, 5))
    choice = {
        team: random.choice([True, False])
    }
    print(choice)
    return choice"""

"""if __name__ == '__main__':
    workers = list()
    teams = [i for i in range(5)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(test_scoring, teams)
    scores = list(results)
    print(scores)"""

se = TestScoringEngine(30, 'Team{}')

for i in range(0, 100):
    se.score_services(i+1)

se.export_all_as_csv()