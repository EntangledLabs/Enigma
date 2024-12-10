import tomllib, csv, json
from os.path import join, splitext
from io import TextIOWrapper, BytesIO, StringIO

import requests

from enigma_requests import Box, Credlist, Inject, ParableUser, Team

with open(join('./example_configs/creds', 'examplecreds.csv'), 'r+') as f:
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

with open(join('./example_configs/boxes', 'examplebox.json'), 'rb') as f:
    data = json.load(f)
    print(Box.add(
        Box(
            name='examplebox',
            identifier=data['identifier'],
            config=json.dumps(data)
        )
    )
)
with open(join('./example_configs/boxes', 'examplebox2.json'), 'rb') as f:
    data = json.load(f)
    print(Box.add(
        Box(
            name='examplebox2',
            identifier=data['identifier'],
            config=json.dumps(data)
        )
    ))

with open(join('./example_configs/injects', 'inject1.json'), 'rb') as f:
    data = json.load(f)
    print(Inject.add(
        Inject(
            num=1,
            name=data['name'],
            config=json.dumps(data)
        )
    ))

Team.add(
    Team(
        name='coolname',
        identifier=1
    )
)

Team.add(
    Team(
        name='radname',
        identifier=2
    )
)