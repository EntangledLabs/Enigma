import tomllib, csv
import pkgutil, inspect
import quikscore
import os, hashlib
from quikscore.auth import PWHash
from quikscore.models import User, ScoreReport
from quikscore.database import db_session, init_db, del_db
from quikscore.checks import Service, SSHService, HTTPService, HTTPSService
from quikscore.scoring import Box, ScoringEngine, CredList

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

engine = ScoringEngine(60, 5, 30, 10, 30, 100)