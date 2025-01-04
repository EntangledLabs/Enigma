from contextlib import asynccontextmanager
import uvicorn

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.routing import Router as StarletteRouter, Mount

from parable.logger import log_config, write_log_header
from parable.route import Route, StaticRouter
from parable.routes import index_routes, admin_router, user_router
from parable.auth import ParableAuthBackend
from parable import secret_key


# Lifespan handler
@asynccontextmanager
async def lifespan(app):
    for route in app.router.routes:
        print(route)
        if isinstance(route, Mount):
            if isinstance(route.app, StarletteRouter):
                for mount_route in route.app.routes:
                    print(mount_route)
                    print(mount_route.url_path_for(mount_route.name))
        else:
            print(route.url_path_for(route.name))
    print(app.router)
    print(app.router.url_path_for('token'))
    write_log_header()
    yield

# Routes
app_routes = [
    index_routes,
    admin_router,
    user_router,
    StaticRouter()
]

# Middleware
middleware = [
    #Middleware(AuthenticationMiddleware, backend=ParableAuthBackend),
    #Middleware(SessionMiddleware, secret_key=secret_key)
]

# Application creation
app = Starlette(
    debug=True,
    lifespan=lifespan,
    routes=Route.get_routes(app_routes),
    middleware=middleware
)

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=5070,
        log_config=log_config
    )