from os import getenv, getcwd
from os.path import join

from dotenv import load_dotenv

from uvicorn.config import LOGGING_CONFIG

load_dotenv(override=True)

#### Creates a universal logger for Parable

log_config = LOGGING_CONFIG

log_level = getenv('LOG_LEVEL')
logs_path = join(getcwd(), 'logs')

log_file = join(logs_path, 'parable.log')

# Writing a header to the log file because it looks better
def write_log_header():
    with open(log_file, 'w+') as f:
        f.writelines([
            '++++==== Parable Web Interface Log ====++++\n'
        ])

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