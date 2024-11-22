import tomllib, csv, json, random
import pkgutil, inspect
import enigma
import os, hashlib
from enigma.auth import PWHash
from enigma.models import Team, ScoreReport, TeamCreds, SLAReport, ScoreHistory, InjectReport
from enigma.database import db_session, init_db, del_db
from enigma.checks import Service, SSHService, HTTPService, HTTPSService
from enigma.scoring import ScoringEngine
from enigma.util import ScoreBreakdown, TeamManager, Box, Inject
from enigma.settings import logs_path, injects_path, test_artifacts_path
import logging

from datetime import datetime

import plotly.express as px
import pandas as pd

from os import listdir
from os.path import isfile, join, splitext

print('deleting tables')
db_session.query(ScoreReport).delete()
db_session.query(TeamCreds).delete()
db_session.query(SLAReport).delete()
db_session.query(ScoreHistory).delete()
db_session.query(InjectReport).delete()
db_session.commit()
db_session.close()

print('finding all comp info')
boxes = ScoringEngine.find_boxes()
services = Box.full_service_list(boxes)
creds = ScoringEngine.find_credlists()
teams = ScoringEngine.find_teams()
managers = ScoringEngine.create_managers(teams, services, creds)
injects = ScoringEngine.find_injects()

rounds = 20

for i in range(1, rounds - 1):
    print('doing round {}'.format(i))
    for team, manager in managers.items():
        for service in services:
            db_session.add(
                ScoreReport(
                    team_id = team,
                    service = service,
                    result = random.choice([True, False])
                )
            )
            db_session.commit()
            db_session.close()
        manager.tabulate_scores(i)
            
print('creating injects')
for team, manager in managers.items():
    for inject in injects:
        scores = {
            'professionalism': random.choice(['troll', 'dreadful', 'poor', 'acceptable', 'exceeds', 'outstanding']),
            'accuracy': random.choice(['fail', 'pass'])
        }
        inject.score_inject(team, scores)

print('doing round {}'.format(rounds))
for team, manager in managers.items():
    for service in services:
        db_session.add(
            ScoreReport(
                team_id = team,
                service = service,
                result = random.choice([True, False])
            )
        )
        db_session.commit()
        db_session.close()
    manager.tabulate_scores(rounds)

print('exporting')
for team, manager in managers.items():
    manager.scores.export_csv('testscores{}'.format(team), test_artifacts_path)