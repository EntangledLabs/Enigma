from nicegui import ui, app
from fastapi import FastAPI

from parable.competitor import router as CompetitorRouter
from parable.admin import router as AdminRouter

def init(fastapi_app: FastAPI) -> None:
    @ui.page('/')
    def index():
        pass

    @ui.page('/dashboard')
    def dashboard():
        pass

    app.include_router(CompetitorRouter)
    app.include_router(AdminRouter)

    ui.run_with(
        fastapi_app
    )