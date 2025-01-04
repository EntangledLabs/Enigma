from starlette.authentication import requires

from parable.route import Router, Route
from parable import templates

user_router = Router(name='user')
admin_router = Router(name='admin')

# Index route
index_routes = Route()

@index_routes.route("/", methods=["GET"])
async def index(request):
    template = "index.html"
    context = {"request": request}
    return templates.TemplateResponse(template, context)