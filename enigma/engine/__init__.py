from os import getenv, getcwd
from dotenv import load_dotenv
from os.path import join

load_dotenv(override=True)

postgres_settings = {
    'user': getenv('POSTGRES_USER'),
    'password': getenv('POSTGRES_PASSWORD'),
    'host': getenv('POSTGRES_HOST'),
    'port': getenv('POSTGRES_PORT')
}

static_path = join(getcwd(), 'static')
checks_path = join(getcwd(), 'enigma')