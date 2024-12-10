import asyncio
import tomllib, json
from datetime import timedelta

from typing import Annotated
from fastapi import FastAPI, HTTPException, Depends, APIRouter, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select, delete
import uvicorn

from engine.database import init_db, get_session, del_db
from engine.scoring import ScoringEngine
from engine.util import FileConfigLoader
from engine import log_config, api_version
from engine.auth import (
    api_key_auth, 
    ParableUser, 
    Token, 
    authenticate_user, 
    get_current_user, 
    create_access_token, 
    permissions_levels,
    ParableUserCreate,
    ParableUserTable,
    get_hash
)
from engine.models import *
from engine import log, access_token_expiration_mins, static_path

# Initialize the DB
log.info('Initializing DB')
init_db()

# Create the scoring engine
FileConfigLoader.load_settings()
FileConfigLoader.load_api_key()
se = ScoringEngine()

# Auth router
user_router = APIRouter(
    prefix='/parableusers',
    tags=['parableusers']
)

# Engine router
engine_router = APIRouter(
    prefix='/engine',
    tags=['engine']
)

# Environment routers
box_router = APIRouter(
    prefix='/boxes',
    tags=['boxes']
)
team_router = APIRouter(
    prefix='/teams',
    tags=['teams']
)
creds_router = APIRouter(
    prefix='/creds',
    tags=['creds']
)
injects_router = APIRouter(
    prefix='/injects',
    tags=['injects']
)
teamcreds_router = APIRouter(
    prefix='/teamcreds',
    tags=['teamcreds']
)
settings_router = APIRouter(
    prefix='/settings',
    tags=['settings']
)

# Report routers
sla_report_router = APIRouter(
    prefix='/sla-reports',
    tags=['sla-reports']
)
inject_report_router = APIRouter(
    prefix='/inject-reports',
    tags=['inject-reports']
)
score_report_router = APIRouter(
    prefix='/score-reports',
    tags=['score-reports']
)

# Helpers

obi_wan = HTTPException(status_code=400, detail='These aren\'t the rows you are looking for')


################
# Routes for Engine CMD

# Adding engine run commands
@engine_router.post('/start')
async def start_scoring():
    if not se.teams_detected:
        raise HTTPException(status_code=423, detail='No teams detected, cannot start Enigma')
    if se.enginelock:
        raise HTTPException(status_code=423, detail='Enigma is already running!')
    log.info('Starting Enigma scoring')
    asyncio.create_task(se.run())
    return {'ok': True}

@engine_router.post('/update')
async def update_teams():
    if se.enginelock:
        raise HTTPException(status_code=423, detail='Cannot update teams, Enigma is running')
    log.info('Updating teams in Enigma')
    se.find_teams()
    return {'ok': True}

@engine_router.post('/pause')
async def pause_scoring():
    if se.pause or not se.enginelock:
        raise HTTPException(status_code=423, detail='Enigma is already paused!')
    log.info('Pausing Enigma scoring')
    se.pause = True
    return {'ok': True}

@engine_router.post('/unpause')
async def unpause_scoring():
    if not se.pause or not se.enginelock:
        raise HTTPException(status_code=423, detail='Enigma is already unpaused!')
    log.info('Unpausing Enigma scoring')
    se.pause = False
    return {'ok': True}

@engine_router.post('/stop')
async def stop_scoring():
    if not se.enginelock:
        raise HTTPException(status_code=423, detail='Enigma is not running!')
    log.info('Stopping Enigma scoring')
    se.stop = True
    return {'ok': True}

@engine_router.post('/reset')
async def clean_tables(*, session: Session = Depends(get_session)):
    session.exec(delete(BoxTable))
    session.exec(delete(CredlistTable))
    session.exec(delete(InjectTable))
    session.exec(delete(TeamTable))
    session.exec(delete(TeamCredsTable))
    session.exec(delete(SLAReportTable))
    session.exec(delete(InjectReportTable))
    session.exec(delete(ScoreReportTable))
    session.exec(delete(ParableUserTable))
    session.commit()
    return {'ok': True}

@engine_router.post('/hard-reset')
async def hard_reset():
    del_db()
    await asyncio.sleep(2)
    init_db()
    FileConfigLoader.load_api_key()
    return {'ok': True}

@engine_router.post('/reset-data')
async def reset_comp_data(*, session: Session = Depends(get_session)):
    session.exec(delete(SLAReportTable))
    session.exec(delete(InjectReportTable))
    session.exec(delete(ScoreReportTable))
    session.commit()
    se.reset_scores()
    return {'ok': True}

@engine_router.get('/')
async def get_scoring_state():
    return {'running': se.enginelock, 'paused': se.pause}

################
# Routes for CRUD

# Box routes
@box_router.post('/', response_model=BoxPublic)
async def add_box(*, session: Session = Depends(get_session), box: BoxCreate):
    db_box = BoxTable.model_validate(box)
    try:
        session.add(db_box)
        session.commit()
    except:
        raise HTTPException(status_code=400, detail='Cannot add box with non-unique properties!')
    session.refresh(db_box)
    return db_box

@box_router.get('/', response_model=list[BoxPublic])
async def list_boxes(*, session: Session = Depends(get_session)):
    boxes = session.exec(select(BoxTable)).all()
    return boxes

@box_router.get('/{box_name}', response_model=BoxPublic)
async def get_box(*, session: Session = Depends(get_session), box_name: str):
    box = session.exec(select(BoxTable).where(BoxTable.name == box_name)).one()
    if not box:
        raise HTTPException(status_code=404, detail='Box not found')
    return box

@box_router.put('/{box_name}', response_model=BoxPublic)
async def update_box(*, session: Session = Depends(get_session), box_name: str, box: BoxUpdate):
    db_box = session.exec(select(BoxTable).where(BoxTable.name == box_name)).one()
    if not db_box:
        raise HTTPException(status_code=404, detail='Box not found')
    box_data = box.model_dump(exclude_unset=True)
    db_box.sqlmodel_update(box_data)
    try:
        data = tomllib.loads(db_box.config)
        identifier = data['identifier']
    except:
        raise obi_wan
    session.add(db_box)
    session.commit()
    session.refresh(db_box)
    return db_box

@box_router.delete('/{box_name}')
async def delete_box(*, session: Session = Depends(get_session), box_name: str):
    box = session.exec(select(BoxTable).where(BoxTable.name == box_name)).one()
    if not box:
        raise HTTPException(status_code=404, detail='Box not found')
    session.delete(box)
    session.commit()
    return {'ok': True}


# Credlist routes
@creds_router.post('/', response_model=CredlistPublic)
async def add_credlist(*, session: Session = Depends(get_session), credlist: CredlistCreate):
    if se.enginelock:
        raise HTTPException(status_code=423, detail='Enigma is running! Cannot add credlists during the competition')
    db_credlist = CredlistTable.model_validate(credlist)
    try:
        session.add(db_credlist)
        session.commit()
    except:
        raise HTTPException(status_code=400, detail='Cannot add credlist with non-unique properties!')
    session.refresh(db_credlist)
    return db_credlist

@creds_router.get('/', response_model=list[CredlistPublic])
async def list_credlists(*, session: Session = Depends(get_session)):
    credlists = session.exec(select(CredlistTable)).all()
    return credlists

@creds_router.get('/{creds_name}', response_model=CredlistPublic)
async def get_credlist(*, session: Session = Depends(get_session), creds_name: str):
    credlist = session.exec(select(CredlistTable).where(CredlistTable.name == creds_name)).one()
    if not credlist:
        raise HTTPException(status_code=404, detail='Credlist not found')
    return credlist

@creds_router.put('/{creds_name}', response_model=CredlistPublic)
async def update_credlist(*, session: Session = Depends(get_session), creds_name: str, credlist: CredlistUpdate):
    if se.enginelock:
        raise HTTPException(status_code=423, detail='Enigma is running! Cannot update credlists during the competition')
    db_credlist = session.exec(select(CredlistTable).where(CredlistTable.name == creds_name)).one()
    if not db_credlist:
        raise HTTPException(status_code=404, detail='Credlist not found')
    credlist_data = credlist.model_dump(exclude_unset=True)
    db_credlist.sqlmodel_update(credlist_data)
    try:
        json.loads(db_credlist.creds)
    except:
        raise obi_wan
    session.add(db_credlist)
    session.commit()
    session.refresh(db_credlist)
    return db_credlist

@creds_router.delete('/{creds_name}')
async def delete_credlist(*, session: Session = Depends(get_session), creds_name: str):
    if se.enginelock:
        raise HTTPException(status_code=423, detail='Enigma is running! Cannot remove credlists during the competition')
    credlist = session.exec(select(CredlistTable).where(CredlistTable.name == creds_name)).one()
    if not credlist:
        raise HTTPException(status_code=404, detail='Credlist not found')
    session.delete(credlist)
    session.commit()
    return {'ok': True}


# Inject routes
@injects_router.post('/', response_model=InjectPublic)
async def add_inject(*, session: Session = Depends(get_session), inject: InjectCreate):
    db_inject = InjectTable.model_validate(inject)
    try:
        session.add(db_inject)
        session.commit()
    except:
        raise HTTPException(status_code=400, detail='Cannot add inject with non-unique properties!')
    session.refresh(db_inject)
    return db_inject

@injects_router.get('/', response_model=list[InjectPublic])
async def list_injects(*, session: Session = Depends(get_session)):
    injects = session.exec(select(InjectTable)).all()
    return injects

@injects_router.get('/{inject_name}', response_model=InjectPublic)
async def get_inject(*, session: Session = Depends(get_session), inject_name: str):
    inject = session.exec(select(InjectTable).where(InjectTable.name == inject_name)).one()
    if not inject:
        raise HTTPException(status_code=404, detail='Inject not found')
    return inject

@injects_router.put('/{inject_name}', response_model=InjectPublic)
async def update_inject(*, session: Session = Depends(get_session), inject_name: str, inject: InjectUpdate):
    db_inject = session.exec(select(InjectTable).where(InjectTable.name == inject_name)).one()
    if not db_inject:
        raise HTTPException(status_code=404, detail='Inject not found')
    inject_data = inject.model_dump(exclude_unset=True)
    db_inject.sqlmodel_update(inject_data)
    try:
        data = tomllib.loads(db_inject.config)
        name = data['name']
        description = data['description']
        worth = data['worth']
        rubric = data['rubric']
    except:
        raise obi_wan
    session.add(db_inject)
    session.commit()
    session.refresh(db_inject)
    return db_inject

@injects_router.delete('/{inject_name}')
async def delete_inject(*, session: Session = Depends(get_session), inject_name: str):
    inject = session.exec(select(InjectTable).where(InjectTable.name == inject_name)).one()
    if not inject:
        raise HTTPException(status_code=404, detail='Inject not found')
    session.delete(inject)
    session.commit()
    return {'ok': True}


# Team routes
@team_router.post('/', response_model=TeamPublic)
async def add_team(*, session: Session = Depends(get_session), team: TeamCreate):
    if se.enginelock:
        raise HTTPException(status_code=423, detail='Enigma is running! Cannot add teams during the competition')
    db_team = TeamTable.model_validate(team)
    try:
        session.add(db_team)
        session.commit()
    except:
        raise HTTPException(status_code=400, detail='Cannot add team with non-unique properties!')
    session.refresh(db_team)
    se.find_teams()
    return db_team

@team_router.get('/', response_model=list[TeamPublic])
async def list_teams(*, session: Session = Depends(get_session)):
    teams = session.exec(select(TeamTable)).all()
    return teams

@team_router.get('/{team_id}', response_model=TeamPublic)
async def get_team(*, session: Session = Depends(get_session), team_id: int):
    team = session.exec(select(TeamTable).where(TeamTable.identifier == team_id)).one()
    if team is None:
        raise HTTPException(status_code=404, detail='Team not found')
    return team

@team_router.put('/{team_id}', response_model=TeamPublic)
async def update_team(*, session: Session = Depends(get_session), team_id: int, team: TeamUpdate):
    if se.enginelock:
        raise HTTPException(status_code=423, detail='Enigma is running! Cannot modify teams during the competition')
    db_team = session.exec(select(TeamTable).where(TeamTable.identifier == team_id)).one()
    if db_team is None:
        raise HTTPException(status_code=404, detail='Team not found')
    team_data = team.model_dump(exclude_unset=True)
    db_team.sqlmodel_update(team_data)
    session.add(db_team)
    session.commit()
    session.refresh(db_team)
    return db_team

@team_router.delete('/{team_id}')
async def delete_team(*, session: Session = Depends(get_session), team_id: int):
    if se.enginelock:
        raise HTTPException(status_code=423, detail='Enigma is running! Cannot delete teams during the competition')
    team = session.exec(select(TeamTable).where(TeamTable.identifier == team_id)).one()
    if team is None:
        raise HTTPException(status_code=404, detail='Team not found')
    session.delete(team)
    session.commit()
    se.find_teams()
    return {'ok': True}


# TeamCreds routes
@teamcreds_router.get('/{team_id}', response_model=list[TeamCredsPublic])
async def list_teamcreds(*, session: Session = Depends(get_session), team_id: int):
    teamcreds = session.exec(select(TeamCredsTable).where(TeamCredsTable.team_id == team_id)).all()
    return teamcreds

@teamcreds_router.get('/{team_id}/{credlist_name}', response_model=TeamCredsPublic)
async def get_teamcreds(*, session: Session = Depends(get_session), team_id: int, credlist_name: str):
    teamcreds = session.exec(select(TeamCredsTable).where(TeamCredsTable.team_id == team_id).where(TeamCredsTable.name == credlist_name)).one()
    if teamcreds is None:
        raise HTTPException(status_code=404, detail='TeamCreds not found')
    return teamcreds

@teamcreds_router.put('/{team_id}/{credlist_name}', response_model=TeamCredsPublic)
async def update_teamcreds(*, session: Session = Depends(get_session), team_id: int, credlist_name: str, teamcreds: TeamCredsUpdate):
    db_teamcreds = session.exec(select(TeamCredsTable).where(TeamCredsTable.team_id == team_id).where(TeamCredsTable.name == credlist_name)).one()
    if db_teamcreds is None:
        raise HTTPException(status_code=404, detail='TeamCreds not found')
    teamcreds_data = teamcreds.model_dump(exclude_unset=True)
    db_teamcreds.sqlmodel_update(teamcreds_data)
    try:
        json.loads(db_teamcreds.creds)
    except:
        raise obi_wan
    session.add(db_teamcreds)
    session.commit()
    session.refresh(db_teamcreds)
    return db_teamcreds
    

# SLAReport routes
@sla_report_router.get('/{team_id}', response_model=list[SLAReportPublic])
async def list_sla_reports(*, session: Session = Depends(get_session), team_id: int):
    sla_reports = session.exec(select(SLAReportTable).where(SLAReportTable.team_id == team_id)).all()
    return sla_reports


# InjectReport routes
@inject_report_router.post('/', response_model=InjectReportPublic)
async def add_inject_report(*, session: Session = Depends(get_session), inject_report: InjectReportCreate):
    db_inject_report = InjectReportTable.model_validate(inject_report)
    try:
        session.add(db_inject_report)
        session.commit()
    except:
        raise HTTPException(status_code=400, detail='Cannot add inject report with non-unique properties!')
    session.refresh(db_inject_report)
    return db_inject_report

@inject_report_router.get('/{inject_id}', response_model=list[InjectReportPublic])
async def list_inject_reports(*, session: Session = Depends(get_session), inject_id: int):
    inject_reports = session.exec(select(InjectReportTable).where(InjectReportTable.inject_num == inject_id)).all()
    return inject_reports

@inject_report_router.get('/{inject_id}/{team_id}', response_model=InjectReportPublic)
async def get_inject_report(*, session: Session = Depends(get_session), inject_id: int, team_id: int):
    inject_report = session.exec(select(InjectReportTable).where(InjectReportTable.inject_num == inject_id).where(InjectReportTable.team_id == team_id)).one()
    if inject_report is None:
        raise HTTPException(status_code=404, detail='InjectReport not found')
    return inject_report

@inject_report_router.put('/{inject_id}/{team_id}', response_model=InjectReportPublic)
async def update_inject_report(*, session: Session = Depends(get_session), inject_id: int, team_id: int, injectreport: InjectReportUpdate):
    db_inject_report = session.exec(select(InjectReportTable).where(InjectReportTable.inject_num == inject_id).where(InjectReportTable.team_id == team_id)).one()
    if db_inject_report is None:
        raise HTTPException(status_code=404, detail='InjectReport not found')
    inject_report_data = injectreport.model_dump(exclude_unset=True)
    db_inject_report.sqlmodel_update(inject_report_data)
    try:
        json.loads(db_inject_report.breakdown)
    except:
        raise obi_wan
    session.add(db_inject_report)
    session.commit()
    session.refresh(db_inject_report)
    return db_inject_report

@inject_report_router.delete('/{inject_id}/{team_id}')
async def delete_inject_report(*, session: Session = Depends(get_session), inject_id: int, team_id: int):
    inject_report = session.exec(select(InjectReportTable).where(InjectReportTable.inject_num == inject_id).where(InjectReportTable.team_id == team_id)).one()
    if inject_report is None:
        raise HTTPException(status_code=404, detail='InjectReport not found')
    session.delete(inject_report)
    session.commit()
    return {'ok': True}


# ScoreReport routes
@score_report_router.get('/by-round/{round_num}', response_model=list[ScoreReportPublic])
async def list_score_reports_by_round(*, session: Session = Depends(get_session), round_num: int):
    score_reports = session.exec(select(ScoreReportTable).where(ScoreReportTable.round == round_num)).all()
    if score_reports is None:
        raise HTTPException(status_code=404, detail='No score reports found for that round')
    return score_reports

@score_report_router.get('/by-team/{team_id}', response_model=list[ScoreReportPublic])
async def list_score_reports_by_team(*, session: Session = Depends(get_session), team_id: int):
    score_reports = session.exec(select(ScoreReportTable).where(ScoreReportTable.team_id == team_id)).all()
    if score_reports is None:
        raise HTTPException(status_code=404, detail='No score reports found for that team')
    return score_reports

@score_report_router.get('/{team_id}', response_model=ScoreReportPublic)
async def get_latest_score_report(*, session: Session = Depends(get_session), team_id: int):
    score_report = session.exec(select(ScoreReportTable).where(ScoreReportTable.team_id == team_id).order_by(ScoreReportTable.round.desc())).first()
    if score_report is None:
        raise HTTPException(status_code=404, detail='No score reports found for that team')
    return score_report


# Settings routes
@settings_router.get('/', response_model=SettingsPublic)
async def get_settings(*, session: Session = Depends(get_session)):
    settings = session.exec(select(Settings)).one()
    return settings

@settings_router.put('/', response_model=SettingsPublic)
async def update_settings(*, session: Session = Depends(get_session), settings: SettingsUpdate):
    if se.enginelock:
        raise HTTPException(status_code=423, detail='Enigma is running! Cannot modify settings during the competition')
    db_settings = session.exec(select(Settings)).one()
    settings_data = settings.model_dump(exclude_unset=True)
    db_settings.sqlmodel_update(settings_data)
    session.add(db_settings)
    session.commit()
    session.refresh(db_settings)
    return db_settings

################
# Users routes
@user_router.post('/', response_model=ParableUser)
async def create_user(*, session: Session = Depends(get_session), parable_user: ParableUserCreate):
    db_parable_user = ParableUserTable(
        username=parable_user.username,
        identifier=parable_user.identifier,
        permission_level=parable_user.permission_level,
        pwhash=get_hash(parable_user.password)
    )
    try:
        session.add(db_parable_user)
        session.commit()
    except:
        raise HTTPException(status_code=400, detail='Cannot add Parable user with non-unique properties!')
    session.refresh(db_parable_user)
    return db_parable_user

@user_router.get('/', response_model=ParableUser)
async def get_self(current_user: Annotated[ParableUser, Depends(get_current_user)]):
    return current_user

@user_router.get('/perms')
async def get_perms(current_user: Annotated[ParableUser, Depends(get_current_user)]):
    return {'permission_level': current_user.permission_level}

@user_router.get('/user/{username}', response_model=ParableUser)
async def get_user(*, session: Session = Depends(get_session), username: str):
    user = session.exec(select(ParableUserTable).where(ParableUserTable.username == username)).one()
    if user is None:
        raise HTTPException(status_code=404, detail='No user found with that username!')
    return user

@user_router.get('/all', response_model=list[ParableUser])
async def get_all_users(*, session: Session = Depends(get_session)):
    users = session.exec(select(ParableUserTable)).all()
    if users is None:
        raise HTTPException(status_code=404, detail='No users found!')
    return users

@user_router.get('/last-identifier')
async def get_last_identifier(*, session: Session = Depends(get_session)):
    last_user = session.exec(select(ParableUserTable).order_by(ParableUserTable.identifier.desc())).first()
    if last_user is None:
        raise HTTPException(status_code=404, detail='No users found!')
    return {'identifier': last_user.identifier}

@user_router.get('/permission-levels')
async def get_all_levels():
    return permissions_levels

@user_router.delete('/user/{username}')
async def delete_credlist(*, session: Session = Depends(get_session), username: str):
    user = session.exec(select(ParableUserTable).where(ParableUserTable.username == username)).one()
    if user is None:
        raise HTTPException(status_code=404, detail='No user found with that username!')
    session.delete(user)
    session.commit()
    return {'ok': True}

################
# Creating new FastAPI app

log.info('Initializing Enigma')
app = FastAPI(title='Enigma Scoring Engine', summary='Created by Entangled', api_version=api_version)

app.mount('/static', StaticFiles(directory=static_path), name='static')

app.include_router(user_router, prefix=f'/api/v{api_version}', dependencies=[Depends(api_key_auth)])
app.include_router(settings_router, prefix=f'/api/v{api_version}', dependencies=[Depends(api_key_auth)])
app.include_router(engine_router, prefix=f'/api/v{api_version}', dependencies=[Depends(api_key_auth)])

# Adding environment routers
app.include_router(box_router, prefix=f'/api/v{api_version}', dependencies=[Depends(api_key_auth)])
app.include_router(creds_router, prefix=f'/api/v{api_version}', dependencies=[Depends(api_key_auth)])
app.include_router(injects_router, prefix=f'/api/v{api_version}', dependencies=[Depends(api_key_auth)])
app.include_router(team_router, prefix=f'/api/v{api_version}', dependencies=[Depends(api_key_auth)])

# Adding report routers
app.include_router(teamcreds_router, prefix=f'/api/v{api_version}', dependencies=[Depends(api_key_auth)])
app.include_router(sla_report_router, prefix=f'/api/v{api_version}', dependencies=[Depends(api_key_auth)])
app.include_router(inject_report_router, prefix=f'/api/v{api_version}', dependencies=[Depends(api_key_auth)])
app.include_router(score_report_router, prefix=f'/api/v{api_version}', dependencies=[Depends(api_key_auth)])
log.info(f'Started Enigma Scoring Engine with API version v{api_version}')

@app.get('/')
async def read_root():
    return {'ok': True}

@app.post('/token')
async def login(*, session: Session = Depends(get_session), form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token_expiration_time = timedelta(minutes=access_token_expiration_mins)
    access_token = create_access_token(
        data = {
            'sub': user.username
        },
        expires_delta=access_token_expiration_time
    )
    return Token(access_token=access_token, token_type="bearer")


################
if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=4731,
        log_config=log_config
    )