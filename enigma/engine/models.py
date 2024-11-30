from sqlmodel import SQLModel, Field

# Misc
# API only exposes RU
class SettingsBase(SQLModel):
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

class Settings(SettingsBase, table=True):
    __tablename__ = 'settings'
    id: int | None = Field(default=None, primary_key=True)
    log_level: str = Field(default='info')

class SettingsPublic(SettingsBase):
    pass

class SettingsUpdate(SettingsBase):
    competitor_info: str | None = None
    pcr_portal: bool | None = None
    inject_portal: bool | None = None
    comp_name: str | None = None
    check_time: int | None = None
    check_jitter: int | None = None
    check_timeout: int | None = None
    check_points: int | None = None
    sla_requirement: int | None = None
    sla_penalty: int | None = None
    first_octets: str | None = None
    first_pod_third_octet: int | None = None

# Environment info

# Box
class BoxBase(SQLModel):
    name: str = Field(unique=True)
    identifier: int = Field(ge=1, le=255, unique=True)
    config: str

class BoxTable(BoxBase, table=True):
    __tablename__ = 'boxes'
    id: int | None = Field(default=None, primary_key=True)
    
class BoxCreate(BoxBase):
    pass

class BoxPublic(BoxBase):
    id: int

class BoxUpdate(BoxBase):
    name: str | None = None
    identifier: int | None = None
    config: str | None = None

# Credlist
class CredlistBase(SQLModel):
    name: str = Field(unique=True)
    creds: str

class CredlistTable(CredlistBase, table=True):
    __tablename__ = 'credlists'
    id: int | None = Field(default=None, primary_key=True)
    
class CredlistCreate(CredlistBase):
    pass

class CredlistPublic(CredlistBase):
    id: int

class CredlistUpdate(CredlistBase):
    name: str | None = None
    creds: str | None = None

# Inject
class InjectBase(SQLModel):
    num: int = Field(unique=True)
    name: str = Field(unique=True)
    config: str

class InjectTable(InjectBase, table=True):
    __tablename__ = 'injects'
    id: int | None = Field(default=None, primary_key=True)
    
class InjectCreate(InjectBase):
    pass

class InjectPublic(InjectBase):
    id: int

class InjectUpdate(InjectBase):
    num: int | None = None
    name: str | None = None
    config: str | None = None

# Team
class TeamBase(SQLModel):
    name: str = Field(unique=True)
    identifier: int = Field(ge=1, le=255, unique=True)
    score: int

class TeamTable(TeamBase, table=True):
    __tablename__ = 'teams'
    id: int | None = Field(default=None, primary_key=True)
    
class TeamCreate(TeamBase):
    pass

class TeamPublic(TeamBase):
    id: int

class TeamUpdate(TeamBase):
    name: str | None = None
    identifier: int | None = None
    score: int | None = None

# Creds
# API only exposes UG (PCR)
class TeamCredsBase(SQLModel):
    name: str = Field(foreign_key='credlists.name')
    team_id: int = Field(foreign_key='teams.identifier')
    creds: str

class TeamCredsTable(TeamCredsBase, table=True):
    __tablename__ = 'teamcreds'
    id: int | None = Field(default=None, primary_key=True)

class TeamCredsPublic(TeamCredsBase):
    id: int

class TeamCredsUpdate(TeamCredsBase):
    name: str | None = None
    team_id: int | None = None
    creds: str | None = None

# Reports

# SLA reports
# API only exposes G
class SLAReportBase(SQLModel):
    team_id: int = Field(foreign_key='teams.identifier')
    round: int
    service: str

class SLAReport(SLAReportBase, table=True):
    __tablename__ = 'slareports'
    id: int | None = Field(default=None, primary_key=True)
    
class SLAReportPublic(SLAReportBase):
    id: int

# Inject reports
class InjectReportBase(SQLModel):
    team_id: int = Field(foreign_key='teams.identifier')
    inject_num: int = Field(foreign_key='injects.num')
    score: int
    breakdown: str

class InjectReport(InjectReportBase, table=True):
    __tablename__ = 'injectreports'
    id: int | None = Field(default=None, primary_key=True)

class InjectReportCreate(InjectReportBase):
    pass

class InjectReportPublic(InjectReportBase):
    id: int
    
class InjectReportUpdate(InjectReportBase):
    team_id: int | None = None
    inject_num: int | None = None
    score: int | None = None

# Score reports
# API only exposes G
class ScoreReportBase(SQLModel):
    team_id: int = Field(foreign_key='teams.identifier')
    round: int
    score: int

class ScoreReport(ScoreReportBase, table=True):
    __tablename__ = 'scorereports'
    id: int | None = Field(default=None, primary_key=True)

class ScoreReportPublic(ScoreReportBase):
    id: int