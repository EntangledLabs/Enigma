import json

from sqlmodel import SQLModel, Field, Session, select

from enigma.checks import Service

from enigma import possible_services
from enigma.engine.database import db_engine
from enigma.enigma_logger import log


# Box
class BoxDB(SQLModel, table = True):
    __tablename__ = 'boxes'
    name: str = Field(primary_key=True)
    identifier: int = Field(ge=1, le=255, unique=True)
    service_config: str

class Box:

    def __init__(self, name: str, identifier: int, service_config: dict):
        self.name = name
        self.identifier = identifier
        self.service_config = service_config
        self.services = self.compile_services()
        log.debug(f"Created new Box with name {self.name}")

    def __repr__(self):
        return '<Box> named \'{}\' with identifier \'{}\' and services {}'.format(self.name, self.identifier, self.services)
    
    # Get every service for the box in the format 'box.service'
    def get_service_names(self):
        log.debug(f"Finding formatted service names for {self.name}")
        names = list()
        for service in self.compile_services():
            names.append(f'{self.name}.{service.name}')
        return names

    # Takes a dict of service config data and creates new Service objects based off of them
    def compile_services(self) -> list[Service]:
        log.debug(f"Compiling services for {self.name}")
        services = list()
        from_json = self.service_config
        for service, config in from_json.items():
            if service in possible_services.keys():
                services.append(possible_services[service].new(from_json[service]))

        return services

    #######################
    # DB fetch/add

    # Tries to add the box object to the DB. If exists, it will return False, else True
    def add_to_db(self) -> bool:
        log.debug(f"Adding Box {self.name} to database")
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
            log.warning(f"Failed to add Box {self.name} to database!")
            return False
    
    # Fetches all Box from the DB
    @classmethod
    def find_all(cls):
        log.debug(f"Retrieving all boxes from database")
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

    # Gets the names of all the services
    @classmethod
    def all_service_names(cls, boxes: list):
        log.debug("Finding formatted service names for all boxes")
        services = []
        for box in boxes:
            services.extend(
                box.get_service_names()
            )
        return services
    
    # Creates a new Box object based off of DB data
    @classmethod
    def new(cls, name: str, identifier: int, data: str):
        log.debug(f"Creating new Box {name} with identifier {identifier}")
        return cls(
            name=name,
            identifier=identifier,
            service_config=json.loads(data)
        )