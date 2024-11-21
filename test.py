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

services = Box.full_service_list(ScoringEngine.find_boxes())
creds = ScoringEngine.find_credlists()

manager = TeamManager.new(1, services, creds)

for i in range(1, 11):
    db_session.add(
        ScoreReport(
            team_id = 1,
            round = i,
            service = 'examplebox.ssh',
            result = random.choice([True, False])
        )
    )
    db_session.add(
        ScoreReport(
            team_id = 1,
            round = i,
            service = 'examplebox.http',
            result = random.choice([True, False])
        )
    )
    db_session.commit()
    
    manager.tabulate_scores(i)

db_session.close()

manager.scores.export_csv('testscores', './')