from typing import override, Self

from starlette.routing import Route as StarletteRoute, Mount

from parable import static

class ParableRouter:

    def __init__(self, name: str='index', path: str='/') -> None:
        self._routes = []
        self._name = name
        self._path = path
        print()

    def __iter__(self):
        for route in self._routes:
            yield route

    def include_router(self, router: Self) -> None:
        if router._path != '/':
            starlette_mount = Mount(
                path=router._path,
                name=router._name,
                routes=router._routes,
            )
            self._routes.append(starlette_mount)
        else:
            self._routes.extend(router._routes)

    def route(self, path: str, methods: list[str]):
        #print(path, methods)
        def inner(func):
            #print(func, path, methods)
            self._routes.append(
                StarletteRoute(
                    path=path,
                    endpoint=func,
                    methods=methods,
                )
            )
            return func
        return inner