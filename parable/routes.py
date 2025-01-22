from starlette.authentication import requires

from parable.route import ParableRouter

user_router = ParableRouter(name='user', path='/user')
admin_router = ParableRouter(name='admin', path='/admin')