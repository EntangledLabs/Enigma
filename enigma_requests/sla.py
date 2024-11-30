import json

from pydantic import BaseModel, Field
import requests

class SLAReport(BaseModel):
    id: int
    team_id: int
    round: int
    service: str