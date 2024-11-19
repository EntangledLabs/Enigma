from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base

engine = create_engine('sqlite:///quikscore.db')
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    import quikscore.models
    Base.metadata.create_all(bind=engine)

def del_db():
    import quikscore.models
    Base.metadata.drop_all(bind=engine)