from sqlmodel import create_engine, SQLModel, Session

from engine import db_url

db_engine = create_engine(db_url, echo=False)

def get_session():
    with Session(db_engine) as session:
        yield session

def init_db():
    import engine.models
    from engine.auth import APIKey
    SQLModel.metadata.create_all(db_engine)

def del_db():
    import engine.models
    from engine.auth import APIKey
    SQLModel.metadata.drop_all(db_engine)