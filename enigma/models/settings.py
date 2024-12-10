import json

from sqlmodel import SQLModel, Field, Session, select

from enigma.engine.database import db_engine

# Settings
class Settings(SQLModel, table=True):
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
    first_octets: str = Field(nullable=False)
    first_pod_third_octet: int = Field(default=1, ge=1, le=255)

    @classmethod
    def get_setting(cls, key: str):
        with Session(db_engine) as session:
            settings = session.exec(select(Settings)).one()
            return settings[key]