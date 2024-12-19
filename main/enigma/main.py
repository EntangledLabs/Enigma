import sys

from enigma.logger import log, write_log_header

from enigma.engine.cmd import RvBCMD
from enigma.engine.database import del_db, init_db

from enigma.models.settings import Settings

# main.py [OPTIONS]
# -r, --reset   Does a reset of the database
if __name__ == '__main__':

    write_log_header()

    # Initializing and reading arguments
    log.info("Welcome to Enigma Scoring Engine!")
    log.info("Entangled was in pain making this")
    log.info("Enigma Scoring Engine initializing...")
    if sys.argv.__len__() > 1:
        for i in [opt for opt in range(1, len(sys.argv))]:
            arg = sys.argv[i]
            match arg:
                case '-r' | '--reset':
                    log.info("Resetting database...")
                    del_db()
                    init_db()
                case _:
                    pass

    # Creating CMD object
    log.info("Applying default settings...")
    Settings().add_to_db()

    log.info("Enigma Scoring Engine initialized!")
    engine = RvBCMD()

    # Starting CMD listener
    log.info("Listening for commands...")
    engine.start()

    # Shutting down
    log.info("Enigma shutting down, goodbye!")
    raise SystemExit(0)
