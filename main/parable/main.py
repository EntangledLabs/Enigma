from fastapi import FastAPI
import uvicorn

from parable.auth import auth_router
import parable.frontend as frontend

app = FastAPI()

app.include_router(auth_router)

frontend.init(app)

if __name__ == '__main__':
    uvicorn.run(
        app
    )