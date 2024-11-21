import subprocess, random, logging, threading
from abc import ABC, abstractmethod

from enigma.database import db_session

log = logging.getLogger(__name__)

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

    # This method is perhaps most important. It conducts a service check and returns a boolean to represent the result
    # Note that conduct_service_check() will be called in a worker process, not the main thread
    # Implementations of conduct_service_check() must have the identifier and box parameter
    # This is used to properly target a team's box
    # e.x. If the pod networks are on 172.16.<identifier>.0, then conduct_service_check() will target 172.16.<identifier>.<box>
    # e.x. If Team01 has identifier '32', and an SSHService is configured on Box 'examplebox' with host octet 5,
    #      then the worker process will target 172.16.32.5
    @abstractmethod
    def conduct_service_check(self, identifier: int, box: int):
        pass
    
    # Service.new(data) is called to create a new Service object with all of the proper parameters assigned
    # A dict 'data' is passed. Each key in 'data' should refer to a parameter in the __init__
    # e.x. data = {'port': 80} will correspond to Service(port = 80)
    # Default values assignment should be handled here rather than in the __init__
    @classmethod
    @abstractmethod
    def new(cls, data: dict):
        pass

# Service checks

# Performs a simple SSH connection service check
# If a connection is established, the check passes
class SSHService(Service):

    name = 'ssh'

    def __init__(self, credlist: list[str], port: int, auth: list, keyfile: str):
        if not credlist:
            log.critical('Credlist was not defined for SSH, terminating...')
            raise SystemExit(0)
        self.credlist = credlist
        self.port = port
        if auth is None:
            self.auth = ['plaintext']
        else:
            self.auth = auth
        if 'pubkey' in self.auth:
            if keyfile is None:
                log.critical('Pubkey authentication has been selected but no keyfile was given! terminating...')
                raise SystemExit(0)
            self.keyfile = keyfile

    def __repr__(self):
        return '<{}> with port {} and auth methods {}'.format(type(self).__name__, self.port, self.auth)

    def conduct_service_check(self, identifier: int, creds: dict) -> bool:
        log.debug('conducting service check for ssh')
        # TODO: make it not random
        log.warning('Service check for SSH not properly implemented')
        
        return random.choice([True, False])

    @classmethod
    def new(cls, data: dict):
        log.debug('created a SSHService')
        return cls(
            data['credlist'] if 'credlist' in data else None,
            data['port'] if 'port' in data else 22,
            data['auth'] if 'auth' in data else ['plaintext'],
            data['keyfile'] if 'keyfile' in data else None
        )

# Performs a simple HTTP check
# If an HTTP GET request is OK, the check passes
class HTTPService(Service):

    name = 'http'

    def __init__(self, port: int, path: str):
        self.port = port
        if path:
            self.path = path

    def __repr__(self):
        return '<{}> with port {}'.format(type(self).__name__, self.port)

    def conduct_service_check(self, identifier: int) -> bool:
        log.debug('conducting service check for http')
        # TODO: make it not random
        log.warning('Service check for HTTP not properly implemented')
        
        return random.choice([True, False])

    @classmethod
    def new(cls, data: dict):
        log.debug('created a HTTPService')
        return cls(
            data['port'] if 'port' in data else 80,
            data['path'] if 'path' in data else None
        )

# Performs a simple HTTPS check
# If an HTTPS GET request is OK, the check passes
class HTTPSService(Service):

    name = 'https'

    def __init__(self, port: int, path: str):
        self.port = port
        if path:
            self.path = path

    def __repr__(self):
        return '<{}> with port {}'.format(type(self).__name__, self.port)

    def conduct_service_check(self, identifier: int) -> bool:
        log.debug('conducting service check for https')
        # TODO: make it not random
        log.warning('Service check for HTTPS not properly implemented')
        
        return random.choice([True, False])

    @classmethod
    def new(cls, data: dict):
        log.debug('created a HTTPSService')
        return cls(
            data['port'] if 'port' in data else 80,
            data['path'] if 'path' in data else None
        )