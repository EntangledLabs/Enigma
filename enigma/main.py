import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn

from engine.routes import box_router, creds_router, injects_router, team_router, sla_report_router, inject_report_router, score_report_router, settings_router
from engine.database import init_db, del_db

from engine.scoring import ScoringEngine, TestScoringEngine

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Probably want to remove del_db in production
    #del_db()
    #init_db()
    #se = TestScoringEngine(5, 'Team{}')
    #asyncio.create_task(se.run(10))
    yield

# Creating new FastAPI app
app = FastAPI(title='Enigma Scoring Engine', summary='Created by Entangled', lifespan=lifespan)

app.include_router(settings_router)

# Adding environment routers
app.include_router(box_router)
app.include_router(creds_router)
app.include_router(injects_router)
app.include_router(team_router)

# Adding report routers
app.include_router(sla_report_router)
app.include_router(inject_report_router)
app.include_router(score_report_router)

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=4731,
        log_level='info',
        reload=True
    )