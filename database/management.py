from dotenv import load_dotenv
from sqlalchemy import create_engine, Engine
from sqlalchemy.ext.declarative import DeclarativeMeta

import typing as tp

from sqlalchemy_utils import database_exists, create_database # type: ignore
from database.scheme import Base

from env import read_database_credentials_from_env


class CreateEngineAdapter:

    @staticmethod
    def create_engine(database: str, user: str, password: str, host: str, port: tp.Union[str, int],
                      database_name: str) -> Engine:
        return create_engine(
            f'{database}://{user}:{password}@{host}:{port}/{database_name}')


class DatabaseInitializer:
    """Initialize the database and create all the tables"""

    def __init__(self, Base: tp.Type[Base]):
        self.Base = Base

    def initialize(self, database_arguments: tp.Dict[str, tp.Any], recreate: bool = False) -> Engine:

        engine = CreateEngineAdapter.create_engine(**database_arguments)

        if not database_exists(engine.url):
            create_database(engine.url)
        if recreate:
            self.Base.metadata.drop_all(engine)
        self.Base.metadata.create_all(engine)

        return engine


class DatabaseArgumentsLoader:
    """Load arguments from various sources"""

    @staticmethod
    def load_database_arguments(database_type: tp.Literal['TEST', 'PROD']) -> tp.Dict[str, tp.Any]:
        load_dotenv()
        return read_database_credentials_from_env(database_type)
