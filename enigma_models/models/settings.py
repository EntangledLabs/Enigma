from sqlmodel import SQLModel, Field, Session, select, delete

from enigma_models.database import db_engine

# Settings
class SettingsDB(SQLModel, table=True):
    __tablename__ = 'settings'

    id: int | None = Field(default=None, primary_key=True)
    competitor_info: str = Field(default='minimal')
    pcr_portal: bool = Field(default=True)
    inject_portal: bool = Field(default=True)
    comp_name: str = Field(default='example')
    check_time: int = Field(default=30)
    check_jitter: int = Field(default=0, ge=0)
    check_timeout: int = Field(default=5, ge=5)
    check_points: int = Field(default=10, ge=1)
    sla_requirement: int = Field(default=5, ge=1)
    sla_penalty: int = Field(default=100, ge=0)
    first_octets: str = Field(default='10.10')
    first_pod_third_octet: int = Field(default=1, ge=1, le=255)

# Settings class
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
        with Session(db_engine) as session:
            settings = session.exec(select(SettingsDB)).one()
            return getattr(settings, key)