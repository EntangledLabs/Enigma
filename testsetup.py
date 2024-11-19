from enigma.database import db_session, init_db, del_db
from enigma.auth import PWHash
from enigma.models import User

passwords = [User.generate_password() for i in range(0,5)]

with open('testpws.txt', 'w+') as f:
    for i in range(1,6):
        f.writelines(['{},{}\n'.format('Team0{}'.format(i), passwords[i-1])])

del_db()
init_db()

for i in range(1, 6):
    db_session.add(
        User(
            id = i,
            username = 'Team0{}'.format(i),
            pw_hash = PWHash.new(passwords[i-1]),
            identifier = i
        )
    )
    db_session.commit()

db_session.close()