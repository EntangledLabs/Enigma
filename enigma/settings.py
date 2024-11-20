import tomllib
import logging
from datetime import datetime

from dotenv import load_dotenv

from enigma.checks import Service

boxes_path = './boxes/'
creds_path = './creds/'
log_path = './logs/'

points_info = {
    'check_points': 10,
    'sla_penalty': 100
}

possible_services = Service.__subclasses__()

log_level = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warn': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}.get('debug')

log_file = 'enigma_{}.log'.format(datetime.now().strftime('%d_%m_%H_%M'))
