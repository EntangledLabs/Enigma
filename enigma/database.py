import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base

from enigma.settings import db_url
from enigma import is_main

log = logging.getLogger('enigma')

engine = create_engine(db_url)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

if is_main:
    log.info('DB engine has been initialized and session factory is ready')

def init_db():
    import enigma.models
    Base.metadata.create_all(bind=engine)
    log.debug('all tables have been created')

def del_db():
    import enigma.models
    Base.metadata.drop_all(bind=engine)
    log.debug('all tables have been dropped')