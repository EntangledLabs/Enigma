import subprocess, random, logging

from enigma.database import db_session

log = logging.getLogger(__name__)

class Service():

    name = 'empty'

    def __init__(self, port: int=1):
        self.port = port

    def conduct_service_check(self, identifier: int) -> bool:
        return random.choice([True, False])

    @classmethod
    def new(cls, data: dict):
        return cls()

class SSHService(Service):

    name = 'ssh'

    def __init__(self, credlist: list, port: int=22, auth: list=None, keyfile: str=None):
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

    def conduct_service_check(self, identifier: int, creds: dict) -> bool:
        log.debug('conducting service check for ssh')
        # TODO: make it not random
        log.warning('Service check for SSH not properly implemented')
        
        return random.choice([True, False])
    
    def __repr__(self):
        return '<{}> with port {} and auth methods {}'.format(type(self).__name__, self.port, self.auth)

    @classmethod
    def new(cls, data: dict):
        log.debug('created a SSHService')
        return cls(
            data['credlist'],
            data['port'] if 'port' in data else 22,
            data['auth'] if 'auth' in data else None,
            data['keyfile'] if 'keyfile' in data else None
        )

class HTTPService(Service):

    name = 'http'

    def __init__(self, port: int=80, path: str=None):
        self.port = port
        if path:
            self.path = path

    def conduct_service_check(self, identifier: int) -> bool:
        log.debug('conducting service check for http')
        # TODO: make it not random
        log.warning('Service check for HTTP not properly implemented')
        
        return random.choice([True, False])

    def __repr__(self):
        return '<{}> with port {}'.format(type(self).__name__, self.port)

    @classmethod
    def new(cls, data: dict):
        log.debug('created a HTTPService')
        return cls(
            data['port'] if 'port' in data else 80,
            data['path'] if 'path' in data else None
        )

class HTTPSService(Service):

    name = 'https'

    def __init__(self, port: int=443, path: str=None):
        self.port = port
        if path:
            self.path = path

    def conduct_service_check(self, identifier: int) -> bool:
        log.debug('conducting service check for https')
        # TODO: make it not random
        log.warning('Service check for HTTPS not properly implemented')
        
        return random.choice([True, False])

    def __repr__(self):
        return '<{}> with port {}'.format(type(self).__name__, self.port)

    @classmethod
    def new(cls, data: dict):
        log.debug('created a HTTPSService')
        return cls(
            data['port'] if 'port' in data else 80,
            data['path'] if 'path' in data else None
        )