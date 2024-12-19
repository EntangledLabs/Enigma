import sched
import threading

from enigma.logger import log

from enigma.broker import RabbitMQ
from enigma.engine.scoring import ScoringEngine, RvBScoringEngine

# TODO: Add event scheduler to create box score start times
class RvBCMD:

    def __init__(self):
        self.engine = None
        self.rounds = 0
        self.pause = False

    def start(self):
        with RabbitMQ() as rabbit:
            result = rabbit.channel.queue_declare('cmd_queue', exclusive=True)
            rabbit.channel.queue_bind(
                exchange='enigma',
                queue=result.method.queue,
                routing_key='enigma.engine.cmd'
            )
            rabbit.channel.basic_consume(
                queue=result.method.queue,
                on_message_callback=self.on_command_callback,
                auto_ack=True
            )
            try:
                rabbit.channel.start_consuming()
            except KeyboardInterrupt:
                rabbit.channel.stop_consuming()

    def on_command_callback(self, channel, method, properties, body):
        log.info(f'Received command: {body.decode('utf-8')}')
        self.decode_cmd(body.decode('utf-8'))

    # CMD
    # init          creates RvBScoringEngine object
    # update        updates engine with latest info
    # set_rounds    sets the number of rounds to run for - 0 is default, no limit
    # start         starts scoring
    # stop          stops scoring
    # pause         pauses/unpauses scoring
    def decode_cmd(self, cmd):
        cmd_args = cmd.split('.')
        match cmd_args[0]:
            case 'init':
                self.engine = RvBScoringEngine()
                log.info('Created RvB scoring engine object')
            case 'update':
                if isinstance(self.engine, RvBScoringEngine):
                    if not self.engine.engine_lock:
                        self.engine.update_comp()
                        log.info('Updating environment information')
                    else:
                        log.warning('Cannot update comp info while running!')
                else:
                    log.error('Engine does not exist!')
            case 'set_rounds':
                if isinstance(self.engine, RvBScoringEngine):
                    if not self.engine.engine_lock:
                        self.rounds = cmd_args[1]
                        log.info(f'Setting rounds to {self.rounds}')
                    else:
                        log.warning('Cannot change number of rounds while running!')
                else:
                    log.error('Engine does not exist!')
            case 'start':
                if isinstance(self.engine, RvBScoringEngine):
                    if not self.engine.engine_lock:
                        log.info('Starting Enigma Scoring Engine!')
                        threading.Thread(target=self.engine.run, args=(self.rounds,)).start()
                    else:
                        log.warning('Enigma is already running!')
                else:
                    log.error('Engine does not exist!')
            case 'stop':
                if isinstance(self.engine, RvBScoringEngine):
                    if self.engine.engine_lock:
                        log.info('Stopping Enigma Scoring Engine!')
                        self.engine.stop = True
                    else:
                        log.warning('Enigma is not running!')
                else:
                    log.error('Engine does not exist!')
            case 'pause':
                if isinstance(self.engine, RvBScoringEngine):
                    if self.engine.engine_lock:
                        self.pause = not self.pause
                        if self.pause:
                            log.info('Pausing Enigma Scoring Engine!')
                        else:
                            log.info('Unpausing Enigma Scoring Engine!')
                        self.engine.pause = self.pause
                    else:
                        log.warning('Enigma is not running!')
                else:
                    log.error('Engine does not exist!')