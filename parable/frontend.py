from nicegui import ui, app
from fastapi import FastAPI

from .admin import router as AdminRouter
from .theme import frame

from . import (
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