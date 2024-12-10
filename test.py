import json
from os.path import join
import pkgutil, inspect, re
from importlib import import_module

from enigma.models.box import Box
from enigma.engine.database import init_db, del_db
from enigma.engine import possible_services


test_dict_1 = {}
test_dict_2 = {}

print(test_dict_1)
print(test_dict_2)

test_dict_1.update({
    'test1': 'test2'
})

print(test_dict_1)
print(test_dict_2)