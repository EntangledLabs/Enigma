from contextlib import asynccontextmanager
import uvicorn

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.routing import Router as StarletteRouter, Mount, Route

import parable
from parable.logger import log_config, write_log_header
from parable.auth import ParableAuthBackend, auth_routes
from parable import secret_key
from parable import templates, static

# Routes
async def index(request):
    template = "index.html"
    context = {"request": request}
    return templates.TemplateResponse(template, context)

routes = [
    Route('/', endpoint=index),
    Mount('/auth', routes=auth_routes),
    Mount('/static', static, name='static')
]

# Middleware
middleware = [
    #Middleware(AuthenticationMiddleware, backend=ParableAuthBackend),
    #Middleware(SessionMiddleware, secret_key=secret_key)
]

# Lifespan handler
@asynccontextmanager
async def lifespan(app):
    write_log_header()
    print(routes)
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