from os import getcwd
from os.path import join

from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles

templates = Jinja2Templates(directory=join(getcwd(), 'parable', 'templates'))

static = StaticFiles(directory=join(getcwd(), 'parable', 'static'))