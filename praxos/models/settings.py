from sqlmodel import Session, select

from praxos.database import db_engine
from praxos.logger import log

from db_models import SettingsDB

class Settings:

    def __init__(self, **kwargs):
        setting_keys = [
            'id',
            'competitor_info',
            'pcr_portal',
            'inject_portal',
            'comp_name',
            'check_time',
            'check_jitter',
            'check_timeout',
            'check_points',
            'sla_requirement',
            'sla_penalty',
            'first_octets',
            'first_pod_third_octet'
        ]
        for k, v in kwargs.items():
            if k in setting_keys:
                setattr(self, k, v)

    @classmethod
    def get_setting(cls, key: str):
        log.debug(f'Locating setting: {key}')
        with Session(db_engine) as session:
            settings = session.exec(select(SettingsDB)).one()
            return getattr(settings, key)