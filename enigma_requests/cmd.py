import json

from pydantic import BaseModel, Field
import requests

class EnigmaCMD(BaseModel):
    engine_lock: bool
    is_paused: bool