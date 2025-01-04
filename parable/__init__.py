from os import getcwd, getenv
from os.path import join

from dotenv import load_dotenv

from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles

load_dotenv(override=True)

templates = Jinja2Templates(directory=join(getcwd(), 'parable', 'templates'))

static = StaticFiles(directory=join(getcwd(), 'parable', 'static'))

secret_key = getenv('PARABLE_SECRET_KEY')