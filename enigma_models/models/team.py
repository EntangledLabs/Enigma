from sqlmodel import SQLModel, Field, Session, select

from enigma_models.database import db_engine

# Team model
class RvBTeamDB(SQLModel, table=True):
    __tablename__ = 'teams'

    name: str = Field(primary_key=True, foreign_key='parableusers.name')
    identifier: int = Field(ge=1, le=255, unique=True)
    score: int

# Team class
class RvBTeam:

    def __init__(self, name: str, identifier: int, score: int):
        self.name = name
        self.identifier = identifier
        self.score = score

#######################
    # DB fetch/add

    # Tries to add the team object to the DB. If exists, it will return False, else True
    def add_to_db(self):
        try:
            with Session(db_engine) as session:
                session.add(
                    RvBTeamDB(
                        name=self.name,
                        identifier=self.identifier,
                        score=self.score
                    )
                )
                session.commit()
            return True
        except:
            return False

    # Updates score in DB
    def update_in_db(self):
        with Session(db_engine) as session:
            session.exec(
                select(
                    RvBTeamDB
                ).where(
                    RvBTeamDB.identifier == self.identifier
                )
            ).one().score = self.score
            session.commit()

    # Fetches all Team from the DB
    @classmethod
    def find_all(cls):
        teams = []
        with Session(db_engine) as session:
            db_teams = session.exec(
                select(
                    RvBTeamDB
                )
            ).all()
        for db_team in db_teams:
            teams.append(
                RvBTeam(
                    name=db_team.name,
                    identifier=db_team.identifier,
                    score=db_team.score
                )
            )
        return teams

    # Creates a new Team from the config info
    @classmethod
    def new(cls, name: str, identifier: int, score: int):
        return cls(
            name=name,
            identifier=identifier,
            score=score
        )