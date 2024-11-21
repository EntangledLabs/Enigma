import tomllib, csv, json, random
import pkgutil, inspect
import enigma
import os, hashlib
from enigma.auth import PWHash
from enigma.models import Team, ScoreReport, TeamCreds, SLAReport, ScoreHistory
from enigma.database import db_session, init_db, del_db
from enigma.checks import Service, SSHService, HTTPService, HTTPSService
from enigma.scoring import ScoringEngine
from enigma.util import ScoreBreakdown, TeamManager, Box

from datetime import datetime

from os import listdir
from os.path import isfile, join, splitext

db_session.query(ScoreReport).delete()
db_session.query(TeamCreds).delete()
db_session.query(SLAReport).delete()
db_session.query(ScoreHistory).delete()

boxes = ScoringEngine.find_boxes()
services = Box.full_service_list(boxes)
creds = ScoringEngine.find_credlists()
teams = ScoringEngine.find_teams()
managers = ScoringEngine.create_managers(teams, services, creds)

for i in range(1, 11):
    for service in services:
        for team, manager in managers.items():
            db_session.add(
                ScoreReport(
                    team_id = team,
                    round = i,
                    service = service,
                    result = random.choice([True, False])
                )
            )
            db_session.commit()
            db_session.close()

            manager.tabulate_scores(i)
            
for team, manager in managers.items():
    manager.scores.export_csv('testscores', './')

#TeamManager.graph_scores(managers)
