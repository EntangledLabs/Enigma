import tomllib
import logging
from datetime import datetime
from os.path import join

from os import environ

from dotenv import load_dotenv

from enigma.checks import Service

load_dotenv()
with open('./settings.toml', 'rb') as f:
    data = tomllib.load(f)

try:
    boxes_path = data['paths'].get('boxes_path')
    creds_path = data['paths'].get('creds_path')
    logs_path = data['paths'].get('logs_path')
    injects_path = data['paths'].get('injects_path')
    test_artifacts_path = data['paths'].get('test_artifacts_path')

    db_url = environ('DB_URL')

    comp_info = {
        'name': data['general'].get('name'),
        'pcr_portal': data['general'].get('pcr_portal'),
        'inject_portal': data['general'].get('inject_portal'),
        'competitor_info_level': data['general'].get('competitor_info')
    }

    points_info = {
        'check_points': data['round'].get('check_points'),
        'sla_penalty': data['round'].get('sla_penalty'),
        'sla_requirement': data['round'].get('sla_requirement')
    }

    round_info = {
        'check_time': data['round'].get('check_time'),
        'check_jitter': data['round'].get('check_jitter'),
        'check_timeout': data['round'].get('check_timeout')
    }

    possible_services = Service.__subclasses__()

    log_level = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warn': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }.get(data['general'].get('log_level'))

    log_file = join(logs_path, 'enigma_{}.log'.format(datetime.now().strftime('%d_%m_%H_%M_%S'))
    )

    log_output = data['general'].get('log_to')

    max_logs = data['general'].get('max_logs')

    env_info = {
        'first_octet': int(data['environment'].get('first_octets').split('.')[0]),
        'second_octet': int(data['environment'].get('first_octets').split('.')[1]),
        'first_pod': data['environment'].get('first_pot_third_octet')
    }

except:
    raise RuntimeError(
        'Improperly configured settings.toml'
    )