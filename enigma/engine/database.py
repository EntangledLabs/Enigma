from sqlmodel import create_engine, SQLModel

from engine.settings import db_url

db_engine = create_engine(db_url, echo=False)

def init_db():
    import engine.models
    from engine.auth import APIKey
    SQLModel.metadata.create_all(db_engine)

def del_db():
    import engine.models
    from engine.auth import APIKey
    SQLModel.metadata.drop_all(db_engine)