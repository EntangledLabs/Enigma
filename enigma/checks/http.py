import random
import time

from enigma.checks import Service
from enigma.enigma_logger import log

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

    def conduct_service_check(self, addr: str) -> tuple[bool, str]:
        # TODO: make it not random
        log.warning('Check is not fully implemented! Results are random')
        log.info('Conducting http service check')
        time.sleep(random.randint(1,10))
        result = random.choice([True, False])
        return result, 'randomly generated message'

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

    def conduct_service_check(self, addr: str) -> tuple[bool, str]:
        # TODO: make it not random
        log.warning('Check is not fully implemented! Results are random')
        log.info('Conducting https service check')
        time.sleep(random.randint(1,10))
        result = random.choice([True, False])
        return result, 'randomly generated message'

    @classmethod
    def new(cls, data: dict):
        return cls(
            data['port'] if 'port' in data else 80,
            data['path'] if 'path' in data else None
        )