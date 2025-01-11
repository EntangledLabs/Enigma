import json, csv
from os.path import join, isfile, splitext
from os import listdir

from enigma_models.database import del_db, init_db

from enigma.models.box import Box
from enigma.models.team import RvBTeam
from enigma_models.models.user import ParableUser
from enigma_models.models.settings import Settings
from enigma_models.models.credlist import Credlist
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
teams = []
users = []
for i in range(5):
    user = ParableUser(
        username=f'coolteam{i+1}',
        identifier=i+1,
        permission_level=2
    )
    pw = user.create_pw(12)
    users.append((user, pw))
    user.add_to_db()

    team = RvBTeam(
        name=f'coolteam{i+1}',
        identifier=i+1,
        services=Box.all_service_names(boxes)
    )
    teams.append(team)
    team.add_to_db()

admin_user = ParableUser(
    username='admin',
    identifier=0,
    permission_level=0
)
admin_pw = admin_user.create_pw(12)
users.append((admin_user, admin_pw))
admin_user.add_to_db()

Settings(first_octets='10.10', sla_requirement=2).add_to_db()

print([(user[0].username, user[1]) for user in users])

while True:
    cmd = input('Enter command: ')
    with RabbitMQ() as rabbit:
        rabbit.channel.basic_publish(
            exchange='enigma',
            routing_key='enigma.engine.cmd',
            body=cmd
        )