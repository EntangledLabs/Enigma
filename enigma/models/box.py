import json

from sqlmodel import SQLModel, Field, Session, select

from enigma.engine.database import db_engine
from enigma.engine import possible_services

# Box
class BoxDB(SQLModel, table = True):
    __tablename__ = 'boxes'
    name: str = Field(primary_key=True)
    identifier: int = Field(ge=1, le=255, unique=True)
    service_config: str

class Box():

    def __init__(self, name: str, identifier: int, service_config: dict):
        self.name = name
        self.identifier = identifier
        self.service_config = service_config
        self.services = self.compile_services()

    def __repr__(self):
        return '<Box> named \'{}\' with identifier \'{}\' and services {}'.format(self.name, self.identifier, self.services)
    
    # Get every service for the box in the format 'box.service'
    def get_service_names(self):
        names = list()
        for service in self.compile_services():
            names.append(f'{self.name}.{service.name}')
        return names

    # Takes a dict of service config data and creates new Service objects based off of them
    def compile_services(self):
        services = list()

        from_json = self.service_config
        for service, config in from_json.items():
            if service in possible_services.keys():
                services.append(possible_services[service].new(from_json[service]))

        return services
    
    # Tries to add the box object to the DB. If exists, it will return False, else True
    def add_to_db(self):
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