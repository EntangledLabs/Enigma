from os import getenv
import tomllib, tomli_w, json

from dotenv import load_dotenv
from pydantic import BaseModel, Field

import requests

load_dotenv(override=True)

api_url = getenv('API_URL')
api_version = getenv('API_VERSION')

headers = {
    "Content-Type": "application/json",
    "X-API-KEY": getenv('API_KEY')
}

api_tags = {
    'settings': '/settings/',
    'box': '/boxes/',
    'creds': '/creds/',
    'inject': '/injects/',
    'team': '/teams/',
    'sla': '/sla-reports/',
    'inject-report': '/inject-reports/',
    'score': '/score-reports/',
    'engine': '/engine/',
    'user': '/parableusers/'

}

def enigma_path(tag: str, index: int=None, num: int=None, specific1=None, specific2=None):
    return (
        api_url
        + f'v{api_version}'
        + api_tags[tag]
        + (
            f'{specific2}/' if specific2 is not None else ''
        )
        + (
            f'{specific1}' if specific1 is not None else ''
        )
        + (
            f'?offset={index}&limit={num}' if index is not None and num is not None else ''
        )
    )

def dump_toml(path: str):
    with open(path, 'rb') as f:
        return tomli_w.dumps(tomllib.load(f))
    
# Settings
class Settings(BaseModel):
    competitor_info: str
    pcr_portal: bool
    inject_portal: bool
    comp_name: str
    check_time: int
    check_jitter: int
    check_timeout: int
    check_points: int
    sla_requirement: int
    sla_penalty: int
    first_octets: str
    first_pod_third_octet: int

    @classmethod
    def get(cls):
        settings_data = requests.get(enigma_path('settings'), headers=headers)
        return Settings.model_validate_json(settings_data.text)
    
    @classmethod
    def update(cls, settings: dict[str: any]):
        return requests.put(enigma_path('settings'), json=settings, headers=headers)
    
# Box
class Box(BaseModel):
    name: str
    identifier: int = Field(ge=1, le=255)
    config: str

    @classmethod
    def add(cls, box):
        if isinstance(box, Box):
            return requests.post(enigma_path('box'), json=box.model_dump(), headers=headers)
        return False

    @classmethod
    def list(cls, index: int=0, num: int=10):
        results = []
        boxes_data = requests.get(enigma_path('box', index=index, num=num), headers=headers).text
        boxes_data = json.loads(boxes_data)
        for box in boxes_data:
            results.append(
                Box.model_validate(box)
            )
        return results
    
    @classmethod
    def get(cls, name: str):
        box_data = requests.get(enigma_path('box', specific1=name), headers=headers)
        return Box.model_validate_json(box_data.text)
    
    @classmethod
    def update(cls, name: str, box: dict):
        return requests.put(enigma_path('box', specific1=name), json=box, headers=headers)
    
    @classmethod
    def delete(cls, name: str):
        return requests.delete(enigma_path('box', specific1=name), headers=headers)

# Credlist
class Credlist(BaseModel):
    name: str
    creds: str

    @classmethod
    def add(cls, creds):
        if isinstance(creds, Credlist):
            return requests.post(enigma_path('creds'), json=creds.model_dump(), headers=headers)
        return False

    @classmethod
    def list(cls, index: int=0, num: int=10):
        results = []
        creds_data = requests.get(enigma_path('creds', index=index, num=num), headers=headers).text
        creds_data = json.loads(creds_data)
        for creds in creds_data:
            results.append(
                Credlist.model_validate(creds)
            )
        return results
    
    @classmethod
    def get(cls, name: str):
        creds_data = requests.get(enigma_path('creds', specific1=name), headers=headers)
        return Credlist.model_validate_json(creds_data.text)
    
    @classmethod
    def update(cls, name: str, creds: dict):
        return requests.put(enigma_path('creds', specific1=name), json=creds, headers=headers)
    
    @classmethod
    def delete(cls, name: str):
        return requests.delete(enigma_path('creds', specific1=name), headers=headers)

# Inject
class Inject(BaseModel):
    num: int
    name: str
    config: str

    @classmethod
    def add(cls, inject):
        if isinstance(inject, Inject):
            return requests.post(enigma_path('inject'), json=inject.model_dump(), headers=headers)
        return False

    @classmethod
    def list(cls, index: int=0, num: int=10):
        results = []
        injects_data = requests.get(enigma_path('inject', index=index, num=num), headers=headers).text
        injects_data = json.loads(injects_data)
        for inject in injects_data:
            results.append(
                Inject.model_validate(inject)
            )
        return results
    
    @classmethod
    def get(cls, name: str):
        injects_data = requests.get(enigma_path('inject', specific1=name), headers=headers)
        return Inject.model_validate_json(injects_data.text)
    
    @classmethod
    def update(cls, name: str, inject: dict):
        return requests.put(enigma_path('inject', specific1=name), json=inject, headers=headers)
    
    @classmethod
    def delete(cls, name: str):
        return requests.delete(enigma_path('inject', specific1=name), headers=headers)
    
# Team
class Team(BaseModel):
    name: str
    identifier: int = Field(ge=1, le=255)
    score: int

    @classmethod
    def add(cls, team):
        if isinstance(team, Team):
            return requests.post(enigma_path('team'), json=team.model_dump(), headers=headers)
        return False

    @classmethod
    def list(cls, index: int=0, num: int=10):
        results = []
        teams_data = requests.get(enigma_path('team', index=index, num=num), headers=headers).text
        teams_data = json.loads(teams_data)
        for team in teams_data:
            results.append(
                Team.model_validate(team)
            )
        return results
    
    @classmethod
    def get(cls, team_id: int):
        teams_data = requests.get(enigma_path('team', specific1=team_id), headers=headers)
        return Team.model_validate_json(teams_data.text)
    
    @classmethod
    def update(cls, team_id: int, team: dict):
        return requests.put(enigma_path('team', specific1=team_id), json=team, headers=headers)
    
    @classmethod
    def delete(cls, team_id: int):
        return requests.delete(enigma_path('team', specific1=team_id), headers=headers)
    
# SLA Reports
class SLAReport(BaseModel):
    team_id: int
    round: int
    service: str

    @classmethod
    def list(cls, team_id: int, index: int=0, num: int=10):
        results = []
        sla_data = requests.get(enigma_path('sla', index=index, num=num, specific1=team_id), headers=headers).text
        sla_data = json.loads(sla_data)
        for sla_report in sla_data:
            results.append(
                SLAReport.model_validate(sla_report)
            )
        return results
    
# Inject Reports
class InjectReport(BaseModel):
    team_id: int
    inject_num: int
    score: int
    breakdown: str

    @classmethod
    def add(cls, inject_report):
        if isinstance(inject_report, InjectReport):
            return requests.post(enigma_path('inject-report'), json=inject_report.model_dump(), headers=headers)
        return False

    @classmethod
    def list(cls, inject_id: int, index: int=0, num: int=10):
        results = []
        inject_report_data = requests.get(enigma_path('inject-report', index=index, num=num, specific1=inject_id), headers=headers).text
        inject_report_data = json.loads(inject_report_data)
        for inject_report in inject_report_data:
            results.append(
                InjectReport.model_validate(inject_report)
            )
        return results
    
    @classmethod
    def get(cls, inject_id: int, team_id: int):
        inject_report_data = requests.get(enigma_path('inject-report', specific1=team_id, specific2=inject_id), headers=headers)
        return InjectReport.model_validate_json(inject_report_data.text)
    
    @classmethod
    def update(cls, inject_id: int, team_id: int, inject_report: dict):
        return requests.put(enigma_path('inject-report', specific1=team_id, specific2=inject_id), json=inject_report, headers=headers)
    
    @classmethod
    def delete(cls, inject_id: int, team_id: int):
        return requests.delete(enigma_path('inject-report', specific1=team_id, specific2=inject_id), headers=headers)

# Score Reports
class ScoreReport(BaseModel):
    team_id: int
    round: int
    score: int

    @classmethod
    def list_by_round(cls, round_num: int, index: int=0, num: int=10):
        results = []
        score_report_data = requests.get(enigma_path('score', index=index, num=num, specific1=round_num, specific2='by-round'), headers=headers).text
        score_report_data = json.loads(score_report_data)
        for score_report in score_report_data:
            results.append(
                ScoreReport.model_validate(score_report)
            )
        return results
    
    @classmethod
    def list_by_team(cls, team_id: int, index: int=0, num: int=10):
        results = []
        score_report_data = requests.get(enigma_path('score', index=index, num=num, specific1=team_id, specific2='by-team'), headers=headers).text
        score_report_data = json.loads(score_report_data)
        for score_report in score_report_data:
            results.append(
                ScoreReport.model_validate(score_report)
            )
        return results
    
    @classmethod
    def get(cls, team_id: int):
        score_report_data = requests.get(enigma_path('score', specific1=team_id), headers=headers)
        return ScoreReport.model_validate_json(score_report_data.text)

# Engine commands
class EnigmaCMD(BaseModel):
    running: bool
    paused: bool

    @classmethod
    def start(cls):
        return requests.post(enigma_path('engine', specific1='start'), headers=headers)
    
    @classmethod
    def pause(cls):
        return requests.post(enigma_path('engine', specific1='puase'), headers=headers)

    @classmethod
    def unpause(cls):
        return requests.post(enigma_path('engine', specific1='unpause'), headers=headers)
    
    @classmethod
    def stop(cls):
        return requests.post(enigma_path('engine', specific1='stop'), headers=headers)
    
    @classmethod
    def update_teams(cls):
        return requests.post(enigma_path('engine', specific1='update'), headers=headers)
    
    @classmethod
    def get_state(cls):
        engine_data = requests.get(enigma_path('engine'), headers=headers)
        return EnigmaCMD.model_validate_json(engine_data.text)

# Parable
class ParableUser(BaseModel):
    username: str
    identifier: int
    permission_level: int
    password: str | None = None

    @classmethod
    def add(cls, user):
        if isinstance(user, cls):
            return requests.post(enigma_path('user'), json=user.model_dump(), headers=headers)
        return False
    
    @classmethod
    def delete(cls, username: str):
        return requests.delete(enigma_path('user', specific1=username, specific2='user'), headers=headers)
    
    @classmethod
    def permissions(cls) -> dict:
        perms = requests.get(enigma_path('user', specific1='permission-levels'), headers=headers).text
        perms = json.loads(perms)
        return perms
    
    @classmethod
    def last_identifier(cls) -> int:
        last_identifier = requests.get(enigma_path('user', specific1='last-identifier'), headers=headers).text
        last_identifier = json.loads(last_identifier)
        return int(last_identifier['identifier'])