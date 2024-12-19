from sqlmodel import Session, select

from db_models import RvBTeamDB

from praxos.logger import log
from praxos.database import db_engine

class RvBTeam:

    def __init__(self, name: str, identifier: int, score: int):
        self.name = name
        self.identifier = identifier
        self.score = score

    # Tries to add the team object to the DB. If exists, it will return False, else True
    def add_to_db(self) -> bool:
        log.debug(f'Adding Team {self.name} to database')
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
            log.warning(f'Failed to add Team {self.name} to database!')
            return False

    # Tries to remove the team object from the DB. If it doesn't exist, it will return False, else True
    def remove_from_db(self) -> bool:
        log.debug(f'Removing Team {self.name} from database')
        try:
            with Session(db_engine) as session:
                team = session.exec(
                    select(
                        RvBTeamDB
                    ).where(
                        RvBTeamDB.name == self.name
                    )
                ).one()
                session.delete(team)
                session.commit()
        except:
            log.warning(f'Failed to remove Team {self.name} from database!')
            return False
        return True

    # Fetches all Team from the DB
    @classmethod
    def find_all(cls) -> list:
        log.debug(f'Retrieving all teams from database')
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