from dotenv import load_dotenv
from sqlalchemy import create_engine, Engine

import typing as tp

from sqlalchemy_utils import database_exists, create_database

from database.scheme import Base
from env import read_database_credentials_from_env


class EngineCreator:
    def __init__(self):
        pass

    @staticmethod
    def create_engine(database: str, user: str, password: str, host: str, port: tp.Union[str, int],
                      database_name: str) -> Engine:
        return create_engine(
            f'{database}://{user}:{password}@{host}:{port}/{database_name}')

    @staticmethod
    def create_test_database() -> Engine:
        return EngineCreator.create_engine(
            database="postgresql+psycopg2",
            user="user",
            password="secret",
            host="localhost",
            port=5432,
            database_name="test_database"
        )


class DatabaseInitializer:

    def initalize(self, database_arguments: tp.Dict, recreate: bool = False) -> Engine:

        engine = EngineCreator.create_engine(**database_arguments)

        if not database_exists(engine.url):
            create_database(engine.url)
        if recreate:
            Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

        return engine


class DatabaseArgumentsLoader:
    """Load arguments from various sources"""

    @staticmethod
    def load_database_arguments(database_type: str):
        load_dotenv()
        return read_database_credentials_from_env(database_type)
