import logging

from enigma.settings import log_file, log_level

with open(log_file, 'w+') as f:
    f.writelines([
        '++++==== Enigma Scoring Engine Log ====++++\n'
    ])

logging.basicConfig(
    filename = log_file,
    encoding = 'utf-8',
    filemode = 'a',
    format = '{asctime} {levelname}: {message}',
    style = '{',
    datefmt = '%Y-%m-%dT%H:%M:%S',
    level = log_level
)