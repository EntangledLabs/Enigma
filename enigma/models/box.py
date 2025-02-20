import json

from sqlmodel import Session, select

from enigma.checks import Service

from enigma import possible_services
from enigma.logger import log

from enigma_models.models.box import Box as BoxModel

# Box
class Box(BoxModel):

    def __init__(self, name: str, identifier: int, service_config: dict):
        super().__init__(name, identifier, service_config)
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

    # Gets the names of all the services
    @classmethod
    def all_service_names(cls, boxes: list):
        services = []
        for box in boxes:
            services.extend(
                box.get_service_names()
            )
        return services

    @classmethod
    def find_all(cls):
        boxes = []
        db_boxes = super().find_all()
        for db_box in db_boxes:
            boxes.append(
                Box(
                    name=db_box.name,
                    identifier=db_box.identifier,
                    service_config=db_box.service_config
                )
            )
        return boxes