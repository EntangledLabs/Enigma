from enigma.database import db_session, init_db, del_db
from enigma.auth import PWHash
from enigma.util import Box
from enigma.models import Team
from enigma.scoring import ScoringEngine
from enigma.settings import test_artifacts_path

from os.path import join

################ IMPORTANT ################
# This script will setup 5 teams and their associated records
# This is for testing and development purposes ONLY
# Do not run in production, if you do by accident, call del_db first

num_test_users = 5
team_format = 'Team0{}'

del_db()
init_db()

passwords = [Team.generate_password() for i in range(0, num_test_users)]

with open(join(test_artifacts_path, 'testpws.txt'), 'w+') as f:
    for i in range(1,6):
        f.writelines(['{},{}\n'.format(team_format.format(i), passwords[i-1])])

hashed_passwords = dict()
for i in range(0, num_test_users):
    hashed_passwords.update({
        i+1: PWHash.new(passwords[i-1])
    })

ScoringEngine.create_teams(1, team_format, hashed_passwords)

boxes = ScoringEngine.find_boxes()
services = Box.full_service_list(boxes)
teams = ScoringEngine.find_teams()

print('##### testsetup.py #####')
print('Set up five test users with passwords in testpws.txt\n')

for box in boxes:
    print(box)
print()

print('All services being scored are: {}\n'.format(services))

for team in teams:
    print(team)

db_session.close()