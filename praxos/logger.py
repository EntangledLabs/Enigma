import logging
from os import getenv, getcwd
from os.path import join

from dotenv import load_dotenv

load_dotenv(override=True)

#### Creates a universal logger for Praxos

log_level = getenv('LOG_LEVEL')
logs_path = join(getcwd(), 'logs')

log_file = join(logs_path, 'praxos.log')

# Writing a header to the log file because it looks better
def write_log_header():
    with open(log_file, 'w+') as f:
        f.writelines([
            '++++==== Praxos Discord Bot for Enigma Log ====++++\n'
        ])

# Creating the logger
log = logging.getLogger('praxos')
log.setLevel(log_level)

# Log format
log_format = logging.Formatter(
    '{asctime} {levelname}: {message}',
    datefmt = '%Y-%m-%d %H:%M:%S',
    style = '{'
    )

# Handlers for file and stream output
file_handler = logging.FileHandler(
    log_file,
    mode = 'a',
    encoding = 'utf-8'
    )
file_handler.setFormatter(log_format)

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_format)
console_handler.setLevel(logging.INFO)

log.addHandler(file_handler)
log.addHandler(console_handler)