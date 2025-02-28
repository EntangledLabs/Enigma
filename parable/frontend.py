from nicegui import ui, app
from fastapi import FastAPI

from parable.competitor import router as CompetitorRouter
from parable.admin import router as AdminRouter
from parable.theme import frame
import parable.auth as auth
import parable.login

from parable import secret_key

def init(app: FastAPI) -> None:

    @ui.page('/')
    def homepage():
        with frame('Home Page'):
            ui.label('Welcome to Parable!')

    @auth.page('/dashboard')
    def dashboard():
        with frame('Dashboard'):
            pass

    app.include_router(CompetitorRouter)
    app.include_router(AdminRouter)

    ui.run_with(
        app=app,
        storage_secret=secret_key
    )