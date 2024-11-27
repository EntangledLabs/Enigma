from sqlmodel import create_engine, SQLModel, Session

from engine.settings import db_url

connect_args = {"check_same_thread": False}
db_engine = create_engine(db_url, echo=True, connect_args=connect_args)

def init_db():
    import engine.models
    SQLModel.metadata.create_all(db_engine)

def del_db():
    import engine.models
    SQLModel.metadata.drop_all(db_engine)