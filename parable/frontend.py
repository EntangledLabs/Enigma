from nicegui import ui, app
from fastapi import FastAPI

from parable.competitor import router as CompetitorRouter
from parable.admin import router as AdminRouter
from parable.theme import frame
from parable.auth import AuthMiddleware
from parable import secret_key

def init(app: FastAPI) -> None:


    @ui.page('/dashboard')
    def dashboard():
        with frame('Home Page'):
            pass

    app.include_router(CompetitorRouter)
    app.include_router(AdminRouter)

    app.add_middleware(AuthMiddleware)

    ui.run_with(
        app=app,
        storage_secret=secret_key
    )