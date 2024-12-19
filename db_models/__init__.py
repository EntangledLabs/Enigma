from sqlmodel import SQLModel, Field

# Box
class BoxDB(SQLModel, table = True):
    __tablename__ = 'boxes'

    name: str = Field(primary_key=True)
    identifier: int = Field(ge=1, le=255, unique=True)
    service_config: str

# Credlist
class CredlistDB(SQLModel, table=True):
    __tablename__ = 'credlists'

    name: str = Field(primary_key=True)
    creds: str

# TeamCreds
class TeamCredsDB(SQLModel, table=True):
    __tablename__ = 'teamcreds'

    name: str = Field(foreign_key='credlists.name', primary_key=True)
    team_id: int = Field(foreign_key='teams.identifier', primary_key=True)
    creds: str

# Inject
class InjectDB(SQLModel, table=True):
    __tablename__ = 'injects'

    id: int = Field(primary_key=True)
    name: str = Field(unique=True)
    desc: str
    worth: int
    path: str | None = None
    rubric: str

# InjectReport
class InjectReportDB(SQLModel, table=True):
    __tablename__ = 'injectreports'

    team_id: int = Field(foreign_key='teams.identifier', primary_key=True)
    inject_num: int = Field(foreign_key='injects.id', primary_key=True)
    score: int
    breakdown: str

# Score reports
class ScoreReportDB(SQLModel, table=True):
    __tablename__ = 'scorereports'

    team_id: int = Field(foreign_key='teams.identifier', primary_key=True)
    round: int = Field(primary_key=True)
    score: int
    msg: str

# SLA Report
class SLAReportDB(SQLModel, table=True):
    __tablename__ = 'slareports'

    team_id: int = Field(foreign_key='teams.identifier', primary_key=True)
    round: int = Field(primary_key=True)
    service: str = Field(primary_key=True)

# Team
class RvBTeamDB(SQLModel, table=True):
    __tablename__ = 'teams'

    name: str = Field(primary_key=True, foreign_key='parableusers.name')
    identifier: int = Field(ge=1, le=255, unique=True)
    score: int

# ParableUser
class ParableUserDB(SQLModel, table=True):
    __tablename__ = 'parableusers'

    name: str = Field(primary_key=True)
    identifier: int = Field(ge=1, le=255, unique=True)
    permission_level: int = Field(ge=0, le=2)
    pw_hash: bytes | None = Field(default=None)

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