from contextlib import asynccontextmanager
import uvicorn

from fastapi import FastAPI
from fastapi.routing import APIRoute

from parable.auth import get_token, ParableAuthBackend
from parable.logger import write_log_header, log_config
import parable.frontend as frontend

# Lifespan handler
@asynccontextmanager
async def lifespan(app):
    write_log_header()
    yield

# Application object creation
app = FastAPI(
    debug=True,
    lifespan=lifespan
)

# Adding NiceGUI app on top of existing FastAPI app
frontend.init(app)

# Script run check
if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='localhost',
        port=5070,
        log_config=log_config
    )