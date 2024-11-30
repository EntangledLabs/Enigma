import json

from pydantic import BaseModel, Field
import requests

class Inject(BaseModel):
    id: int
    num: int
    name: str
    config: str

class InjectReport(BaseModel):
    id: int
    team_id: int
    inject_num: int
    score: int
    breakdown: str