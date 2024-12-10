import random
from abc import ABC, abstractmethod

import asyncio

from engine import log

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

# Service checks

# Performs a random check
class RandomService(Service):

    name = 'random'

    def __repr__(self):
        return '<{}> which will randomly give you a pass/fail'.format(type(self).__name__)

    def __eq__(self, obj):
        if isinstance(obj, RandomService):
            return True
        return False

    async def conduct_service_check(self, data: dict):
        log.info('Conducting Random service check')
        await asyncio.sleep(random.randint(1,10))
        result = random.choice([True, False])
        if result:
            return (
                data['team'],
                data['service'],
                'message'
            )
        return
    
    @classmethod
    def new(cls, data: dict):
        return cls()

# Performs a simple SSH connection service check
# If a connection is established, the check passes
class SSHService(Service):

    name = 'ssh'

    def __init__(self, credlist: list[str], port: int, auth: list[str], keyfile: str):
        if not credlist:
            raise SystemExit(0)
        self.credlist = credlist
        self.port = port
        if auth is None:
            self.auth = ['plaintext']
        else:
            self.auth = auth
        if 'pubkey' in self.auth:
            if keyfile is None:
                raise SystemExit(0)
            self.keyfile = keyfile
        log.debug('created SSHService object')

    def __repr__(self):
        return '<{}> with port {} and auth methods {}'.format(type(self).__name__, self.port, self.auth)
    
    def __eq__(self, obj):
        if isinstance(obj, SSHService):
            if (self.port == obj.port
                and self.credlist == obj.credlist
                and self.auth == obj.auth
            ):
                if hasattr(self, 'keyfile') and hasattr(obj, 'keyfile'):
                    if self.keyfile == obj.keyfile:
                        return True
        return False

    async def conduct_service_check(self, data: dict):
        # TODO: make it not random
        log.warning('Check is not fully implemented! Results are random')
        log.info('Conducting ssh service check')
        await asyncio.sleep(random.randint(1,10))
        result = random.choice([True, False])
        if result:
            return (
                data['team'],
                data['service'],
                'message'
            )
        return

    @classmethod
    def new(cls, data: dict):
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
    
    def __eq__(self, obj):
        if isinstance(obj, HTTPService):
            if self.port == obj.port:
                if hasattr(self, 'path') and hasattr(obj, 'path'):
                    if self.path == obj.path:
                        return True
                else:
                    return True
        return False

    async def conduct_service_check(self, data: dict):
        # TODO: make it not random
        log.warning('Check is not fully implemented! Results are random')
        log.info('Conducting http service check')
        await asyncio.sleep(random.randint(1,10))
        result = random.choice([True, False])
        if result:
            return (
                data['team'],
                data['service'],
                'message'
            )
        return
    @classmethod
    def new(cls, data: dict):
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
    
    def __eq__(self, obj):
        if isinstance(obj, HTTPSService):
            if self.port == obj.port:
                if hasattr(self, 'path') and hasattr(obj, 'path'):
                    if self.path == obj.path:
                        return True
                else:
                    return True
        return False

    async def conduct_service_check(self, data: dict):
        # TODO: make it not random
        log.warning('Check is not fully implemented! Results are random')
        log.info('Conducting https service check')
        await asyncio.sleep(random.randint(1,10))
        result = random.choice([True, False])
        if result:
            return (
                data['team'],
                data['service'],
                'message'
            )
        return
    @classmethod
    def new(cls, data: dict):
        return cls(
            data['port'] if 'port' in data else 80,
            data['path'] if 'path' in data else None
        )