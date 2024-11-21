import logging

from enigma.settings import log_file, log_level, log_output


#### Creates a universal logger for Enigma

# Writing a header to the log file because it looks better
with open(log_file, 'w+') as f:
    f.writelines([
        '++++==== Enigma Scoring Engine Log ====++++\n'
    ])

# Creating the logger
log = logging.getLogger(__name__)
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

if 'file' in log_output:
    log.addHandler(file_handler)
if 'console' in log_output:
    log.addHandler(console_handler)