import logging
from os import getenv, getcwd
from dotenv import load_dotenv
from os.path import join
from datetime import datetime

from uvicorn.config import LOGGING_CONFIG

load_dotenv(override=True)

db_url = getenv('DB_URL')

api_key = getenv('API_KEY')
api_version = '1.1.0'

secret_key = getenv('ENIGMA_SECRET_KEY')
access_token_expiration_mins = 30

log = logging.getLogger('uvicorn.error')

logs_path = join(getcwd(), 'logs')
scores_path = join(getcwd(), 'scores')

log_file = join(logs_path, 'enigma_{}.log'.format(datetime.now().strftime('%d_%m_%H_%M_%S')))

with open(log_file, 'w') as f:
    f.writelines([
        '++++==== Enigma Scoring Engine Log ====++++\n'
    ])

log_config = LOGGING_CONFIG
log_config['formatters'].update({
    'file': {
        '()': 'uvicorn.logging.DefaultFormatter',
        'fmt': '{asctime} {levelprefix} {message}',
        'datefmt': '%Y-%m-%d %H:%M:%S',
        'style': '{',
        'use_colors': False
    }
})
log_config['handlers'].update({
    'file': {
        'formatter': 'file',
        'class': 'logging.FileHandler',
        'mode': 'a',
        'filename': log_file
    }
})
log_config['loggers']['uvicorn']['handlers'].append(
    'file'
)
log_config['loggers']['uvicorn.access']['handlers'].append(
    'file'
)