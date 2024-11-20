import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base

log = logging.getLogger(__name__)

engine = create_engine('sqlite:///enigma.db')
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

log.info('db engine has been initialized and session factory is ready')

def init_db():
    import enigma.models
    Base.metadata.create_all(bind=engine)
    log.info('all tables have been created')

def del_db():
    import enigma.models
    Base.metadata.drop_all(bind=engine)
    log.info('all tables have been dropped')