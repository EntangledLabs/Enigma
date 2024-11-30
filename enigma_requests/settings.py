import json

from pydantic import BaseModel, Field
import requests

from . import enigma_path

class Settings(BaseModel):
    log_level: str
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
    def get(self):
        settings_data = requests.get(enigma_path('/settings/'))
        print(settings_data.text)