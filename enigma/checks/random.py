import random
import time

from enigma.checks import Service
from enigma.enigma_logger import log

# Performs a random check
class RandomService(Service):

    name = 'random'

    def __repr__(self):
        return '<{}> which will randomly give you a pass/fail'.format(type(self).__name__)

    def __eq__(self, obj):
        if isinstance(obj, RandomService):
            return True
        return False

    def conduct_service_check(self, addr: str) -> tuple[bool, str]:
        log.info('Conducting Random service check')
        time.sleep(random.randint(1,10))
        result = random.choice([True, False])
        return (result, 'randomly generated message')
    
    @classmethod
    def new(cls, data: dict):
        return cls()