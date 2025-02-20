from contextlib import asynccontextmanager
import uvicorn

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.routing import Router as StarletteRouter, Mount, Route
from starlette.responses import FileResponse

import parable
from parable.logger import log_config, write_log_header
from parable.auth import ParableAuthBackend, auth_routes
from parable import secret_key
from parable import templates, static
from parable.dashboard import dashboard

# Routes
async def index(request):
    template = "index.html"
    context = {"request": request}
    return templates.TemplateResponse(template, context)

async def favicon(request):
    return FileResponse('static/favicon.ico')

routes = [
    Route('/', endpoint=index),
    #Route('/favicon.ico', endpoint=favicon),
    Route('/dashboard', endpoint=dashboard, methods=['GET']),
    Mount('/auth', routes=auth_routes),
    Mount('/static', static, name='static')
]

# Middleware
middleware = [
    Middleware(AuthenticationMiddleware, backend=ParableAuthBackend())
]

# Lifespan handler
@asynccontextmanager
async def lifespan(app):
    write_log_header()
    yield

# Application creation
app = Starlette(
    debug=True,
    lifespan=lifespan,
    routes=routes,
    middleware=middleware
)

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=5070,
        log_config=log_config
    )