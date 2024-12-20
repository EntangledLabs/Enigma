from sqlmodel import create_engine

from parable import postgres_settings

db_engine = create_engine(
    f'postgresql+psycopg://{postgres_settings['user']}:{postgres_settings['password']}@{postgres_settings['host']}:{postgres_settings['port']}/enigma',
    echo=False
)