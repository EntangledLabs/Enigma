from bot.settings import log_file
import logging

with open(log_file, 'w') as f:
    f.writelines([
        '++++==== Enigma Discord Bot Log ====++++\n'
    ])

# Creating the logger
log = logging.getLogger('discord')
log.setLevel(logging.INFO)

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

log.info('Enigma Discord Bot initialized')