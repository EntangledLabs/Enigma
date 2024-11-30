from dotenv import load_dotenv

from os import getenv
from urllib.parse import urljoin

load_dotenv(override=True)

api_url = getenv('API_URL')

def enigma_path(path: str):
    return urljoin(api_url, path)