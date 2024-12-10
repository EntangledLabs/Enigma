import random
from abc import ABC, abstractmethod

# Abstract class Service
# All services are derived from Service
# Add any Service classes to this file or to a file importing Service from enigma.checks
class Service(ABC):

    # Attribute name should be the name of the service
    # name = 'service'

    # The __init__ must contain the specified parameters for the service
    # __init__ should test the parameters for proper use and raise a log.critical() if something isn't right
    @abstractmethod
    def __init__(self):
        pass
    
    # A custom string representation is used for logging
    # The current format used is:
    # <(class name)> with (key params here)
    @abstractmethod
    def __repr__(self):
        pass

    # Custom equivalence used for updating key environment details
    @abstractmethod
    def __eq__(self, obj):
        pass

    # This method is perhaps most important. It conducts a service check and returns a boolean to represent the result
    # Note that conduct_service_check() will be called in a worker process, not the main thread
    # Implementations of conduct_service_check() must check kwargs for check info
    # This is used to properly target a team's box
    # e.x. If the pod networks are on 172.16.<identifier>.0, then conduct_service_check() will target 172.16.<identifier>.<box>
    # e.x. If Team01 has identifier '32', and an SSHService is configured on Box 'examplebox' with host octet 5,
    #      then the worker process will target 172.16.32.5
    @abstractmethod
    async def conduct_service_check(self, **kwargs):
        pass
    
    # Service.new(data) is called to create a new Service object with all of the proper parameters assigned
    # A dict 'data' is passed. Each key in 'data' should refer to a parameter in the __init__
    # e.x. data = {'port': 80} will correspond to Service(port = 80)
    # Default values assignment should be handled here rather than in the __init__
    @classmethod
    @abstractmethod
    def new(cls, data: dict):
        pass