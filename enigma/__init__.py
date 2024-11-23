import logging

from os.path import isfile, join, splitext

from os import remove, listdir

from enigma.settings import log_file, log_level, log_output, logs_path, max_logs


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
console_handler.setLevel(logging.INFO)

if 'file' in log_output:
    log.addHandler(file_handler)
if 'console' in log_output:
    log.addHandler(console_handler)

if max_logs != 0:
    log_files = [f for f in listdir(logs_path) if isfile(join(logs_path, f)) and splitext(f)[-1].lower() == '.log']
    log_files = sorted(log_files)
    while len(log_files) > max_logs:
        remove(join(logs_path, log_files.pop(0)))

log.info('Enigma module initialized')