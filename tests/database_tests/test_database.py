from dotenv import load_dotenv
from sqlalchemy_utils import database_exists, create_database  # type: ignore

from database.management import CreateEngineAdapter, DatabaseInitializer
from database.scheme import Base
from env import read_database_credentials_from_env


class TestDatabase:
    def test_engine_creator(self):
        engine = CreateEngineAdapter.create_engine(database="postgresql", user="USER",
                                                   password="<PASSWORD>", host="<HOST>",
                                                   port=5555, database_name="<DB_NAME>")
        # <PASSWORD> is hidden in engine.url method
        assert str(engine.url) == "postgresql://USER:***@<HOST>:5555/<DB_NAME>"

    def test_database_creation(self):
        load_dotenv()
        database_arguments = read_database_credentials_from_env("TEST")

        engine = DatabaseInitializer(Base=Base).initialize(database_arguments, recreate=False)
        assert database_exists(engine.url)
