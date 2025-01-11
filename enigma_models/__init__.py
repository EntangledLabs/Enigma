from os import getenv
from dotenv import load_dotenv

load_dotenv(override=True)

postgres_settings = {
    'user': getenv('POSTGRES_USER'),
    'password': getenv('POSTGRES_PASSWORD'),
    'host': getenv('POSTGRES_HOST'),
    'port': getenv('POSTGRES_PORT')
}