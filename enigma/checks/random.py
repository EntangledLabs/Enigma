import asyncio, random

from enigma.checks import Service
from enigma.engine.logging import log

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