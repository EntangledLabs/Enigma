import json

from enigma.checks import Service

###################################################
# Class Box
# Represents a box and its services
class Box():

    def __init__(self, name: str, identifier: int, services: list[Service]):
        self.name = name
        self.identifier = identifier
        self.services = services

    def __repr__(self):
        return '<{}> named \'{}\' with services {}'.format(type(self).__name__, self.name, self.services)
    
    def __eq__(self, obj):
        if isinstance(obj, Box):
            if self.name == obj.name and self.identifier == obj.identifier:
                if self.services == obj.services:
                    return True
        return False

    # Get every service for the box in the format 'box.service'
    def get_service_names(self):
        names = list()
        for service in self.services:
            names.append(f'{self.name}.{service.name}')
        return names

    # Takes a dict of service config data and creates new Service objects based off of them
    @classmethod
    def compile_services(cls, data: dict):
        services = list()
        for service in Service.__subclasses__():
            if service.name in data:
                services.append(service.new(data[service.name]))
        return services
    
    # Performs get_service_names() for every box in the list
    @classmethod
    def full_service_list(cls, boxes: list):
        services = list()
        for box in boxes:
            services.extend(box.get_service_names())
        return services

    # Creates a new Box object from a config file or string
    @classmethod
    def new(cls, name:str, data: str):
        data = json.loads(data)
        box = cls(
            name=name,
            identifier=data['identifier'],
            services=cls.compile_services(data)
        )
        return box