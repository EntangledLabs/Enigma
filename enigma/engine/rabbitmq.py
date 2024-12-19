import pika

from enigma.engine import rabbitmq_settings

class RabbitMQ:

    def __init__(self):
        self.user = rabbitmq_settings['user']
        self.password = rabbitmq_settings['password']
        self.host = rabbitmq_settings['host']
        self.port = rabbitmq_settings['port']
        self.connection = None
        self.channel = None
        self.connect()

    def connect(self):
        credentials = pika.PlainCredentials(self.user, self.password)
        parameters = pika.ConnectionParameters(
            host=self.host,
            port=self.port,
            credentials=credentials
        )
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()

    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()

    def consume(self, queue_name: str, callback):
        if not self.channel:
            raise Exception('Connection is not established')
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=callback,
            auto_ack=True
        )
        self.channel.start_consuming()

    def publish(self, queue_name, message: str):
        if not self.channel:
            raise Exception('Connection is not established')
        self.channel.queue_declare(queue=queue_name, durable=True)
        self.channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2
            )
        )
