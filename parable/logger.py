from os import getenv, getcwd
from os.path import join

from dotenv import load_dotenv

load_dotenv(override=True)

#### Creates a universal logger for Enigma

log_level = getenv('LOG_LEVEL')
logs_path = join(getcwd(), 'logs')

log_file = join(logs_path, 'parable.log')

# Writing a header to the log file because it looks better
def write_log_header():
    with open(log_file, 'w+') as f:
        f.writelines([
            '++++==== Parable Web Interface Log ====++++\n'
        ])

# Creating log config
log_config = {
    'version': 1,
    'formatters': {
        'default': {
            'format': '{asctime} {levelname}: {message}',
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'style': '{',
        }
    },
    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': log_file,
            'mode': 'a',
            'encoding': 'utf-8',
            'formatter': 'default',
            'maxBytes': 50000,
            'backupCount': 5,
        }
    },
    'root': {
        'level': log_level,
        'handlers': ['wsgi', 'file', 'stream']
    }
}