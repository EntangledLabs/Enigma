from contextlib import asynccontextmanager
import uvicorn

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.requests import Request

from parable.logger import log_config, write_log_header
from parable.route import Route, StaticRouter
from parable import templates

# Lifespan handler
@asynccontextmanager
async def lifespan(app):
    print(app.router.routes)
    write_log_header()
    yield

# Index route
index_routes = Route()

@index_routes.route("/", methods=["GET"])
async def index(request):
    template = "index.html"
    context = {"request": request}
    return templates.TemplateResponse(template, context)

# All routes
app_routes = [
    index_routes,
    StaticRouter()
]

# Application creation
app = Starlette(
    debug=True,
    lifespan=lifespan,
    routes=Route.get_routes(app_routes)
)

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=5070,
        log_config=log_config
    )