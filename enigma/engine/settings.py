from os import getenv, getcwd
from dotenv import load_dotenv
from os.path import join
from datetime import datetime

from uvicorn.config import LOGGING_CONFIG

load_dotenv(override=True)

db_url = getenv('DB_URL')
api_key = getenv('API_KEY')
api_version = '1.0.1'

#boxes_path = join(getcwd(), 'boxes')        # Path to boxes config directory
#creds_path = './creds/'                     # Path to creds config directory
logs_path = join(getcwd(), 'logs')           # Path to logs config directory
#injects_path = './injects/'                 # Path to injects config directory
#test_artifacts_path = './test_artifacts/'   # Path to test artifacts directory (only used for testing)
#scores_path = './scores/'                   # Path to scores directory

not_found_response = {404: {'description': 'Not found'}}

log_file = join(logs_path, 'enigma_{}.log'.format(datetime.now().strftime('%d_%m_%H_%M_%S')))

open(log_file, 'x')

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