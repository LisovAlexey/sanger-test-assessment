import pytest
from sqlalchemy.orm import sessionmaker

from database.database import DatabaseLayer
from database.init_db import EngineCreator, Base


@pytest.fixture(scope="module")
def engine():
    engine = EngineCreator.create_test_database()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield engine


@pytest.fixture(scope="module")
def database_connection(engine):
    connection = engine.connect()
    yield connection

    connection.close()


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


@pytest.fixture(scope="function")
def sample_one(database_layer):
    # The database_layer does not need to be rolled back because sessions are already rolled back
    yield database_layer.record_receipt(customer_sample_name="test", tube_barcode="NT123")


@pytest.fixture(scope="function")
def sample_two(database_layer):
    yield database_layer.record_receipt(customer_sample_name="test second sample", tube_barcode="NT333")
