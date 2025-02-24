from contextlib import asynccontextmanager
import uvicorn

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.routing import Route

from parable.auth import get_token, ParableAuthBackend
from parable.logger import write_log_header, log_config
import parable.frontend as frontend

# Routes
routes = [
    Route('/get_token', endpoint=get_token, methods=['POST'])
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

# Application object creation
app = Starlette(
    debug=True,
    lifespan=lifespan,
    routes=routes,
    middleware=middleware
)

# Adding NiceGUI app on top of existing Starlette app
frontend.init(app)

# Script run check
if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='localhost',
        port=5070,
        log_config=log_config
    )