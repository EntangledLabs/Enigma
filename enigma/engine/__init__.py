from os import getenv, getcwd
from dotenv import load_dotenv
from os.path import join

load_dotenv(override=True)

postgres_settings = {
    'competitor': getenv('POSTGRES_USER'),
    'password': getenv('POSTGRES_PASSWORD'),
    'host': getenv('POSTGRES_HOST'),
    'port': getenv('POSTGRES_PORT')
}

rabbitmq_settings = {
    'competitor': getenv('RABBITMQ_DEFAULT_USER'),
    'password': getenv('RABBITMQ_DEFAULT_PASSWORD'),
    'host': getenv('RABBITMQ_HOST'),
    'port': 5672
}

static_path = join(getcwd(), 'static')
checks_path = join(getcwd(), 'enigma')