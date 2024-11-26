from engine.database import init_db, del_db
from engine.scoring import ScoringEngine

del_db()
init_db()

se = ScoringEngine()