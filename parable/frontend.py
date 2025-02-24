from nicegui import ui, app
from starlette.applications import Starlette

from parable.competitor import router as CompetitorRouter
from parable.admin import router as AdminRouter
from parable.theme import frame

def init(app: Starlette) -> None:


    @ui.page('/dashboard')
    def dashboard():
        with frame('Home Page'):
            pass

    app.include_router(CompetitorRouter)
    app.include_router(AdminRouter)

    ui.run_with(
        app=app
    )