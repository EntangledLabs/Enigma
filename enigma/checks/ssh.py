import asyncio, random

from enigma.checks import Service
from enigma.engine.logging import log

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