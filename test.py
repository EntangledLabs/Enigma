import json
from os.path import join
import pkgutil, inspect, re
from importlib import import_module

from enigma.models.box import Box
from enigma.engine.database import init_db, del_db
from enigma.engine import possible_services


del_db()
init_db()

print(possible_services)

file_path = join('./example_configs/boxes', 'examplebox.json')
with open(file_path, 'r+') as f:
    data = json.load(f)
    print(data)
    box = Box(name='examplebox', identifier=data['identifier'], service_config=data['services'])
    print(box)
    print(box.services)