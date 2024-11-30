import json

from pydantic import BaseModel, Field
import requests

class Team(BaseModel):
    id: int
    name: str
    identifier: int = Field(ge=1, le=255)
    score: int