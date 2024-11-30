import json

from pydantic import BaseModel, Field
import requests

class ScoreReport(BaseModel):
    id: int
    team_id: int
    round: int
    score: int