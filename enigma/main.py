import asyncio

from fastapi import FastAPI, HTTPException
import uvicorn

from engine.routes import box_router, creds_router, injects_router, team_router, sla_report_router, inject_report_router, score_report_router, settings_router
from engine.database import init_db, del_db
from engine.scoring import ScoringEngine
from engine.util import FileConfigLoader
from engine.settings import log_config
from engine import log, _enginelock

# Initialize the DB
log.info('Initializing DB')
del_db()
init_db()

# Create the scoring engine
FileConfigLoader.load_settings()
se = ScoringEngine()

# Creating new FastAPI app
log.info('Initializing Enigma')
app = FastAPI(title='Enigma Scoring Engine', summary='Created by Entangled')

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

# Adding engine run commands
@app.post('/engine/start')
async def start_scoring():
    if not se.teams_detected:
        raise HTTPException(status_code=423, detail='No teams detected, cannot start Enigma')
    if _enginelock:
        raise HTTPException(status_code=423, detail='Enigma is already running!')
    log.info('Starting Enigma scoring')
    asyncio.create_task(se.run())
    return {'ok': True}

@app.post('/engine/update')
async def update_teams():
    if _enginelock:
        raise HTTPException(status_code=423, detail='Cannot update teams, Enigma is running')
    log.info('Updating teams in Enigma')
    se.teams = se.find_teams()
    return {'ok': True}

@app.post('/engine/pause')
async def pause_scoring():
    if se.pause or not _enginelock:
        raise HTTPException(status_code=423, detail='Enigma is already paused!')
    log.info('Pausing Enigma scoring')
    se.pause = True
    return {'ok': True}

@app.post('/engine/unpause')
async def unpause_scoring():
    if not se.pause or not _enginelock:
        raise HTTPException(status_code=423, detail='Enigma is already unpaused!')
    log.info('Unpausing Enigma scoring')
    se.pause = False
    return {'ok': True}

@app.post('/engine/stop')
async def stop_scoring():
    if not _enginelock:
        raise HTTPException(status_code=423, detail='Enigma is not running!')
    log.info('Stopping Enigma scoring')
    se.stop = True
    return {'ok': True}

@app.get('/engine')
async def get_scoring_state():
    return {'running': _enginelock, 'paused': se.pause}

@app.get('/')
async def read_root():
    return {'ok': True}

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=4731,
        log_config=log_config
    )
