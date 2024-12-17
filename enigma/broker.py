from os import getenv
from dotenv import load_dotenv

import pika

from enigma.enigma_logger import log

load_dotenv(override=True)

class RabbitMQ:

    def __init__(self):
        self.user = getenv('RABBITMQ_DEFAULT_USER', 'guest')
        self.password = getenv('RABBITMQ_DEFAULT_PASS', 'guest')
        self.host = getenv('RABBITMQ_HOST', 'localhost')
        self.connection = None
        self.channel = None
        self.connect()

        self.channel.exchange_declare(
            exchange='enigma',
            exchange_type='topic'
        )
        log.debug('RabbitMQ connection established')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def connect(self):
        credentials = pika.PlainCredentials(self.user, self.password)
        parameters = pika.ConnectionParameters(
            host=self.host,
            credentials=credentials
        )
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()

    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()