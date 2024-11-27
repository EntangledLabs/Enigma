from engine.database import init_db, del_db, db_engine
from sqlmodel import Session, select
import random
from engine.models import ScoreReport

del_db()
init_db()

with Session(db_engine) as session:
    for i in range(1, 6):
        for j in range(1, 21):
            session.add(
                ScoreReport(
                    team_id = i,
                    round = j,
                    score = random.randint(1,300)
                )
            )
    session.commit()

    team_id = 1
    score_report = session.exec(
        select(ScoreReport).where(
            ScoreReport.team_id == team_id
        ).order_by(ScoreReport.round.desc())
    ).first()
    print(score_report)
    
    