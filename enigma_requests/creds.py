import json

from pydantic import BaseModel, Field
import requests

class Credlist(BaseModel):
    id: int
    name: str
    creds: str