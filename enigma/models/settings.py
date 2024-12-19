from sqlmodel import Session, select, delete

from enigma.engine.database import db_engine
from enigma.logger import log

from db_models import SettingsDB

# Settings
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

    #######################
    # DB fetch/add
    def add_to_db(self):
        log.debug(f'Adding settings to database')
        with Session(db_engine) as session:
            session.exec(delete(SettingsDB))
            session.commit()

            settings = SettingsDB()

            for attr in vars(self):
                setattr(settings, attr, getattr(self, attr))

            session.add(
                SettingsDB()
            )
            session.commit()

    @classmethod
    def get_setting(cls, key: str):
        log.debug(f'Locating setting: {key}')
        with Session(db_engine) as session:
            settings = session.exec(select(SettingsDB)).one()
            return getattr(settings, key)