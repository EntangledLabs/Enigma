import tomllib
import logging
from datetime import datetime
from os.path import join

from dotenv import load_dotenv

from enigma.checks import Service

boxes_path = './boxes/'
creds_path = './creds/'
log_path = './logs/'

points_info = {
    'check_points': 10,
    'sla_penalty': 20,
    'sla_requirement': 2
}

round_info = {
    'check_time': 60,
    'check_jitter': 10,
    'check_timeout': 30
}

possible_services = Service.__subclasses__()

log_level = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warn': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}.get('debug')

log_file = join(log_path, 'enigma_{}.log'.format(datetime.now().strftime('%d_%m_%H_%M_%S'))
)

# Can be 'file' and/or 'console'
log_output = ['file']