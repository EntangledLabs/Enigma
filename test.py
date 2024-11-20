import tomllib, csv, json
import pkgutil, inspect
import enigma
import os, hashlib
from enigma.auth import PWHash
from enigma.models import User, ScoreReport
from enigma.database import db_session, init_db, del_db
from enigma.checks import Service, SSHService, HTTPService, HTTPSService
from enigma.scoring import Box, ScoringEngine, CredList
from enigma.util import ScoreBreakdown

import uuid

from os import listdir
from os.path import isfile, join, splitext


#init_db()

#del_db()

"""new_user = User(
    id = 1,
    username = 'testuser',
    pw_hash = PWHash.new('testpw'),
    score = 50
)"""

"""new_report = ScoreReport(
    id = uuid.uuid4(),
    team_id = 3
)"""

#db_session.add(new_report)
#db_session.commit()

#db_session.add(new_user)
#db_session.commit()
#user = db_session.get(User, 1)
#hash = user.pw_hash

#print(hash == 'testpw')



#db_session.remove()

#temp = ['jello', 'globe']

#print(isinstance(temp, list))

#print(type(uuid.uuid4()))
"""boxes = [f for f in listdir('./boxes/') if isfile(join('./boxes/', f)) and splitext(f)[-1].lower() == '.toml']
print(boxes)

for i in boxes:
    print(splitext(i)[0].lower())"""

"""with open('./boxes/examplebox.toml', 'rb') as f:
    data = tomllib.load(f)

print(data)
print(data['suplex'])"""

"""possible_services = Service.__subclasses__()

ssh = SSHService()
for service in possible_services:
    if isinstance(ssh, service):
        print('is an instance of {}'.format(service.name))"""

"""with open('./boxes/examplebox.toml', 'rb') as f:
    data = tomllib.load(f)

print(type(data['ssh']))
print(data['ssh'])"""

"""boxes = ScoringEngine.find_boxes()

print(boxes)"""

#creds_path = './creds/'
#boxes_path = './boxes/'
"""with open(join(creds_path, path), 'r+') as f:
    data = csv.reader(f)
    creds = dict()
    for row in data:
        creds.update({row[0]: row[1]})

print(creds)"""
#print(name)
#print(name.split('_'))

#print(ScoringEngine.find_domain_creds())
#creds = [f for f in listdir(creds_path) if isfile(join(creds_path, f)) and splitext(f)[-1].lower() == '.csv' and splitext(f)[0].lower() == 'domain']
#print(creds)

#box_files = [f for f in listdir(boxes_path) if isfile(join(boxes_path, f)) and splitext(f)[-1].lower() == '.toml']
#print(box_files)

#credlist = CredList.new('examplecreds.csv')
#print(credlist)

#engine = ScoringEngine(60, 5, 30, 10, 30, 100)

scores = ScoreBreakdown(
    ['ssh', 'http'],
    10,
    100
)

scores.award_service_points('ssh')

for i in range(0, 4):
    scores.award_service_points('http')

scores.add_service('https')

for i in range(0, 12):
    scores.award_service_points('https')

scores.award_inject_points(1, 100)

scores.award_inject_points(2, 30)

scores.award_misc_points(30)

scores.award_sla_penalty('https')

scores.award_misc_penalty(5)

scores.remove_service('http')

scores.export_csv('test', './')