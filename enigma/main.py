import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvicorn

from engine import models
from engine.database import init_db, del_db
from engine.scoring import ScoringEngine, TestScoringEngine

@asynccontextmanager
async def lifespan(app: FastAPI):
    del_db()
    init_db()
    se = TestScoringEngine(5, 'Team{}')
    asyncio.create_task(se.run(10))
    yield

app = FastAPI(title='Enigma Scoring Engine', summary='Created by Entangled', lifespan=lifespan)
app.include_router(models.box_router)

@app.get("/")
async def root():
    return {'message': "Hello World"}

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=4731,
        log_level='info'
    )
