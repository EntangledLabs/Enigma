from nicegui import ui, app
from fastapi import FastAPI

from parable.admin import router as AdminRouter
from parable.theme import frame

from parable import (
    login,
    dashboard,
    homepage
)

from parable import secret_key

def init(app: FastAPI) -> None:
    app.include_router(AdminRouter)

    ui.run_with(
        app=app,
        storage_secret=secret_key
    )