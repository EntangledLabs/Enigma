from typing import override

from starlette.routing import Route as StarletteRoute, Mount

from parable import static

class Route:

    def __init__(self):
        self.routes = []

    def route(self, path: str, methods: list):
        def decorator(func):
            self.routes.append(
                StarletteRoute(
                    path=path,
                    endpoint=func,
                    methods=methods
                )
            )
        return decorator

    def build_routes(self):
        return self.routes

    @classmethod
    def get_routes(cls, routes_list: list):
        all_routes = []
        for route in routes_list:
            if isinstance(route, Route):
                all_routes.extend(route.build_routes())
        return all_routes

class Router(Route):

    def __init__(self, name: str):
        super().__init__()
        self.name = name
        self.path = f'/{name}'

    @override
    def build_routes(self):
        return [Mount(
            path=self.path,
            routes=self.routes
        )]

class StaticRouter(Router):

    def __init__(self):
        super().__init__('static')

    @override
    def build_routes(self):
        return [Mount(
            path=self.path,
            app=static,
            name=self.name
        )]