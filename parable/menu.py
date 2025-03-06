from nicegui import ui, app

def menu() -> None:
    async def logout() -> None:
        app.storage.user.clear()
        ui.navigate.to('/login')

    user = app.storage.user.get('user')
    if user is None:
        ui.link('Dashboard', '/dashboard').classes(replace='text-white')
        ui.link('Login', '/login').classes(replace='text-white')
    else:
        ui.label(user.get('username')).classes(replace='text-white')
        ui.link('Dashboard', '/dashboard').classes(replace='text-white')
        ui.link('Logout', '/logout').classes(replace='text-white')