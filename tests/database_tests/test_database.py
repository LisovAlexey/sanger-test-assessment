from sqlalchemy_utils import database_exists, create_database  # type: ignore

from database.management import EngineCreator
from database.scheme import Base


class TestDatabase:
    def test_engine_creator(self):
        engine = EngineCreator.create_engine(database="postgresql", user="<USER>",
                                             password="<PASSWORD>", host="<HOST>",
                                             port=5555, database_name="<DB_NAME>")
        # <PASSWORD> is hidden in engine.url method
        assert str(engine.url) == "postgresql://<USER>:***@<HOST>:5555/<DB_NAME>"

    def test_database_creation(self):

        engine = EngineCreator.create_test_database()
        if not database_exists(engine.url):
            create_database(engine.url)
        Base.metadata.create_all(engine)
