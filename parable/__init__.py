from os import getenv
from dotenv import load_dotenv

load_dotenv(override=True)

secret_key = getenv('PARABLE_SECRET_KEY')

token_age = 60 * 60