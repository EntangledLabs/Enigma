from os.path import join
import logging
from datetime import datetime

from uvicorn.logging import DefaultFormatter
from uvicorn.config import LOGGING_CONFIG

from .settings import logs_path

log = logging.getLogger('uvicorn.error')

log_file = join(logs_path, 'enigma_{}.log'.format(datetime.now().strftime('%d_%m_%H_%M_%S')))

with open(log_file, 'w+') as f:
    f.writelines([
        '++++==== Enigma Scoring Engine Log ====++++\n'
    ])

filehandler = logging.FileHandler(
    log_file,
    mode = 'a',
    encoding = 'utf-8'
)
filehandler.setFormatter(DefaultFormatter)

log.addHandler(filehandler)

print(LOGGING_CONFIG)
print(type(LOGGING_CONFIG))

_enginelock = False