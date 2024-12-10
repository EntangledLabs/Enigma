from os import getenv, getcwd
from dotenv import load_dotenv
from os.path import join
from datetime import datetime
import re
from pkgutil import walk_packages
from importlib import import_module
import inspect

import enigma.checks
from enigma.checks import Service

load_dotenv(override=True)

db_url = getenv('DB_URL')

logs_path = join(getcwd(), 'logs')
static_path = join(getcwd(), 'static')

log_file = join(logs_path, 'enigma_{}.log'.format(datetime.now().strftime('%d_%m_%H_%M_%S')))

def find_possible_services() -> dict[str: Service]:
    possible_services = {}
    enigma_checks = enigma.checks.__path__
    prefix = enigma.checks.__name__ + '.'
    service_match = re.compile(r'^[a-zA-Z]+Service$')
    name_match = re.compile(r'Service$')

    for importer, modname, ispkg in walk_packages(enigma_checks, prefix=prefix):
        module = import_module(modname)
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and not service_match.match(name) is None:
                possible_services.update({
                    name_match.split(name)[0].lower(): obj
                })
    
    return possible_services

possible_services = find_possible_services()