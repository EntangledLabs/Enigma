import subprocess, random

from enigma.database import db_session
from enigma.models import User

class Service():

    name = 'empty'

    def __init__(self, port: int=1):
        self.port = port

    def conduct_service_check(self) -> bool:
        return random.choice([True, False])

    @classmethod
    def new(cls, data: dict):
        return cls()

class SSHService(Service):

    name = 'ssh'

    def __init__(self, credlist: str, port: int=22, auth: list=None, keyfile: str=None):
        if not credlist:
            raise RuntimeError(
                'No credlist was specified'
            )
        self.credlist = credlist
        self.port = port
        if auth is None:
            self.auth = ['plaintext']
        else:
            self.auth = auth
        if 'pubkey' in self.auth:
            if keyfile is None:
                raise RuntimeError(
                    'Pubkey authentication has been selected but no keyfile was given!'
                )
            self.keyfile = keyfile

    def conduct_service_check(self, team: User) -> bool:
        # TODO: make it not random
        
        
        return random.choice([True, False])
    
    def __repr__(self):
        return '<{}> with port {} and auth methods {}'.format(type(self).__name__, self.port, self.auth)

    @classmethod
    def new(cls, data: dict):
        return cls(
            data['port'] if 'port' in data else 22,
            data['auth'] if 'auth' in data else ['plaintext'],
            data['keyfile'] if 'keyfile' in data else None
        )
        

class HTTPService(Service):

    name = 'http'

    def __init__(self, port: int=80, path: str=None):
        self.port = port
        if path:
            self.path = path

    def conduct_service_check(self, team: User) -> bool:
        # TODO: make it not random
        
        return random.choice([True, False])

    def __repr__(self):
        return '<{}> with port {}'.format(type(self).__name__, self.port)

    @classmethod
    def new(cls, data: dict):
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

    def conduct_service_check(self, team: User) -> bool:
        # TODO: make it not random
        
        return random.choice([True, False])

    def __repr__(self):
        return '<{}> with port {}'.format(type(self).__name__, self.port)

    @classmethod
    def new(cls, data: dict):
        return cls(
            data['port'] if 'port' in data else 80,
            data['path'] if 'path' in data else None
        )