import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
import uvicorn

import discord

from engine.routes import box_router, creds_router, injects_router, team_router, sla_report_router, inject_report_router, score_report_router, settings_router
from engine.database import init_db, del_db
from engine.scoring import ScoringEngine
from engine.util import FileConfigLoader
from engine.settings import discord_api_key
from engine import log

from bot.util import EnigmaClient

# Initialize the DB
log.info('Initializing DB')
del_db()
init_db()

# Load any config files
log.info('Added any existing config files')
FileConfigLoader.load_all()

# Create the scoring engine
se = ScoringEngine()

# Create the discord bot
intents = discord.Intents.default()
intents.message_content = True
bot = EnigmaClient(intents=intents)

async def bot_run():
    try:
        await bot.start(discord_api_key)
    except KeyboardInterrupt:
        await bot.close()

# Lifespan event for any tasks that run on start
@asynccontextmanager
async def lifespan(app: FastAPI):
    
    asyncio.create_task(bot_run())
    yield
    await bot.close()

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

# Adding engine run commands
@app.post('/engine/start')
async def start_scoring():
    if se.is_running:
        raise HTTPException(status_code=423, detail='Enigma is already running!')
    run_engine = asyncio.create_task(se.run())
    return {'ok': True}

@app.post('/engine/pause')
async def pause_scoring():
    if se.pause or not se.is_running:
        raise HTTPException(status_code=423, detail='Enigma is already paused!!')
    se.pause = True
    return {'ok': True}

@app.post('/engine/unpause')
async def unpause_scoring():
    if not se.pause or not se.is_running:
        raise HTTPException(status_code=423, detail='Enigma is already unpaused!')
    se.pause = False
    return {'ok': True}

@app.post('/engine/stop')
async def stop_scoring():
    if not se.is_running:
        raise HTTPException(status_code=423, detail='Enigma is not running!')
    se.stop = True
    return {'ok': True}

@app.get('/engine')
async def get_scoring_state():
    return {'running': se.is_running, 'paused': se.pause}

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=4731,
        log_level='info',
        reload=False
    )
