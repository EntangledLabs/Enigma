from engine.database import init_db, del_db
from engine.scoring import TestScoringEngine

import asyncio

del_db()
init_db()

se = TestScoringEngine(5, 'Team{}')

if __name__ == '__main__':
    asyncio.run(
        se.score_services(1)
    )
    se.export_all_as_csv()