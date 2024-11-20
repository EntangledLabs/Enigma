from enigma.database import db_session, init_db, del_db
from enigma.auth import PWHash
from enigma.util import ScoreBreakdown, Box
from enigma.models import Team
from enigma.scoring import ScoringEngine

passwords = [Team.generate_password() for i in range(0,5)]

with open('testpws.txt', 'w+') as f:
    for i in range(1,6):
        f.writelines(['{},{}\n'.format('Team0{}'.format(i), passwords[i-1])])

boxes = ScoringEngine.find_boxes()
services = Box.full_service_list(boxes)

del_db()
init_db()

db_session.add(
    Team(
        id = 0,
        username = 'Admin',
        pw_hash = PWHash.new('enigma'),
        identifier = 0,
        score = 0
    )
)
db_session.commit()

for i in range(1, 6):
    db_session.add(
        Team(
            id = i,
            username = 'Team0{}'.format(i),
            pw_hash = PWHash.new(passwords[i-1]),
            identifier = i,
            score = 0
        )
    )
    db_session.commit()

teams = ScoringEngine.find_teams()

print('#####')
print('Set up five test users with passwords in testpws.txt\n')

for box in boxes:
    print(box)
print()

print('All services being scored are: {}\n'.format(services))

for team in teams:
    print(team)

db_session.close()