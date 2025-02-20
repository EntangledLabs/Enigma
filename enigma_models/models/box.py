import json

from sqlmodel import SQLModel, Field, Session, select

from enigma_models.database import db_engine

# Box model
class BoxDB(SQLModel, table = True):
    __tablename__ = 'boxes'

    name: str = Field(primary_key=True)
    identifier: int = Field(ge=1, le=255, unique=True)
    service_config: str

# Box class
class Box:

    def __init__(self, name: str, identifier: int, service_config: dict):
        self.name = name
        self.identifier = identifier
        self.service_config = service_config

    #######################
    # DB fetch/add

    # Tries to add the box object to the DB. If exists, it will return False, else True
    def add_to_db(self) -> bool:
        try:
            with Session(db_engine) as session:
                session.add(
                    BoxDB(
                        name=self.name,
                        identifier=self.identifier,
                        service_config=json.dumps(self.service_config)
                    )
                )
                session.commit()
            return True
        except:
            return False

    # Fetches all Box from the DB
    @classmethod
    def find_all(cls):
        boxes = []
        with Session(db_engine) as session:
            db_boxes = session.exec(select(BoxDB)).all()
            for box in db_boxes:
                boxes.append(
                    Box.new(
                        name=box.name,
                        identifier=box.identifier,
                        data=box.service_config
                    )
                )
        return boxes

    # Creates a new Box object based off of DB data
    @classmethod
    def new(cls, name: str, identifier: int, data: str):
        return cls(
            name=name,
            identifier=identifier,
            service_config=json.loads(data)
        )