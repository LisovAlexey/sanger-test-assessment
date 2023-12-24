import pytest
from sqlalchemy.orm import sessionmaker

from database.database import DatabaseLayer
from init_db import EngineCreator, Base


@pytest.fixture(scope="module")
def engine():
    print("setup engine")
    engine = EngineCreator.create_test_database()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield engine


@pytest.fixture(scope="module")
def database_connection(engine):
    connection = engine.connect()
    print("setup connection")
    yield connection

    connection.close()
    print("connection close")


@pytest.fixture(scope="function")
def session(database_connection):
    transaction = database_connection.begin()

    Session = sessionmaker(bind=database_connection)
    session = Session()

    yield session

    session.close()
    transaction.rollback()


@pytest.fixture(scope="function")
def database_layer(session):
    yield DatabaseLayer(session)
