import tomllib, tomli_w, csv, json
from os.path import join, splitext
from io import TextIOWrapper, BytesIO, StringIO

import requests

from enigma_requests import Box, Credlist, Inject, ParableUser

"""with open(join('./example_configs/creds', 'examplecreds.csv'), 'r+') as f:
    data = csv.reader(f)
    creds = dict()
    for row in data:
        creds.update({row[0]: row[1]})
    print(Credlist.add(
        Credlist(
            name='examplecreds',
            creds=json.dumps(creds)
        )
    ))

with open(join('./example_configs/creds', 'examplecreds2.csv'), 'r+') as f:
    data = csv.reader(f)
    creds = dict()
    for row in data:
        creds.update({row[0]: row[1]})
    print(Credlist.add(
        Credlist(
            name='examplecreds2',
            creds=json.dumps(creds)
        )
    ))

with open(join('./example_configs/boxes', 'examplebox.toml'), 'rb') as f:
    tomlreader = tomllib.load(f)
    print(Box.add(
        Box(
            name='examplebox',
            identifier=tomlreader['identifier'],
            config=tomli_w.dumps(tomlreader)
        )
    )
)
with open(join('./example_configs/boxes', 'examplebox2.toml'), 'rb') as f:
    tomlreader = tomllib.load(f)
    print(Box.add(
        Box(
            name='examplebox2',
            identifier=tomlreader['identifier'],
            config=tomli_w.dumps(tomlreader)
        )
    ))

with open(join('./example_configs/injects', 'inject1.toml'), 'rb') as f:
    tomlreader = tomllib.load(f)
    print(Inject.add(
        Inject(
            num=1,
            name=tomlreader['name'],
            config=tomli_w.dumps(tomlreader)
        )
    ))"""

teams = {
    'coolteam': 'sdkjfhglkert',
    'neatteam': 'ywkjhttlkffk',
    'superteam': 'jkghskjlhkpd'
}

csvfile = StringIO()
fieldnames = ['team', 'password']

writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
for team, password in teams.items():
    writer.writerow({'team': team, 'password': password})
csvfile.seek(0)

buffer = BytesIO()
buffer.write(csvfile.getvalue().encode('utf-8'))
buffer.seek(0)
buffer.name = 'users.csv'

print(buffer)