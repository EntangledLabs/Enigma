from sqlmodel import Session, select

from db_models import BoxDB

from praxos.logger import log
from praxos.database import db_engine

class Box:

    def __init__(self, name: str):
        self.name = name

    @classmethod
    def find_all(cls):
        log.debug(f"Retrieving all boxes from database")
        boxes = []
        with Session(db_engine) as session:
            db_boxes = session.exec(select(BoxDB)).all()
            for box in db_boxes:
                boxes.append(
                    Box(
                        name=box.name
                    )
                )
        return boxes