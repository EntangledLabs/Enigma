import tomllib, tomli_w, csv, json
from os.path import join, splitext

from enigma_requests import Box, Credlist

cred_file = 'examplecreds2.csv'

with open(join('./example_configs/creds', cred_file), 'r+') as f:
    data = csv.reader(f)
    creds = dict()
    for row in data:
        creds.update({row[0]: row[1]})
    name = splitext(cred_file)[0].lower()
    Credlist.add(
        Credlist(
            name=name,
            creds=json.dumps(creds)
        )
    )