import tomllib, tomli_w, csv, json
from os.path import join, splitext

from enigma_requests import Box, Credlist, Inject

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
    ))