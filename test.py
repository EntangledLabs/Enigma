import json, csv
from os.path import join, isfile, splitext
from os import listdir

from sqlmodel import create_engine

from enigma.engine.database import del_db, init_db

from enigma.models.box import Box
from enigma.models.settings import Settings
from enigma.models.credlist import Credlist
from enigma.models.team import RvBTeam
from enigma.broker import RabbitMQ

boxes_path = './example_configs/boxes'
creds_path = './example_configs/creds'

if input('Reset DB? ').lower() == 'y':
    del_db()
    init_db()

#print('boxes')
boxes = []
ident = 1
for path in listdir(boxes_path):
    if isfile(join(boxes_path, path)) and splitext(path)[-1].lower() == '.json':
        with open(join(boxes_path, path), 'r') as f:
            box = Box(
                name=splitext(path)[0].lower(),
                identifier=ident,
                service_config=json.load(f)
            )
            boxes.append(box)
            box.add_to_db()
    ident = ident + 1

#print('credlists')
credlists = []
for path in listdir(creds_path):
    if isfile(join(creds_path, path)) and splitext(path)[-1].lower() == '.csv':
        with open(join(creds_path, path), 'r+') as f:
            csvreader = csv.reader(f)
            creds = {}
            for row in csvreader:
                creds.update({
                    row[0]: row[1]
                })
            credlist = Credlist(
                name=splitext(path)[0].lower(),
                creds=creds
            )
            credlists.append(credlist)
            credlist.add_to_db()

#print('teams')
"""teams = []
for i in range(5):
    team = RvBTeam(
        name=f'coolteam{i+1}',
        identifier=i+1,
        services=Box.all_service_names(boxes)
    )
    teams.append(team)
    team.add_to_db()"""

Settings(first_octets='10.10', sla_requirement=2)

while True:
    cmd = input('Enter command: ')
    with RabbitMQ() as rabbit:
        rabbit.channel.basic_publish(
            exchange='enigma',
            routing_key='enigma.engine.cmd',
            body=cmd
        )