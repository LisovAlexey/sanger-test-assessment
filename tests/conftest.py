import pytest
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker

from database.database import DatabaseLayer
from database.management import DatabaseInitializer
from database.scheme import Base
from env import read_database_credentials_from_env


@pytest.fixture(scope="module")
def engine():
    load_dotenv()
    database_arguments = read_database_credentials_from_env("TEST")

    engine = DatabaseInitializer(Base=Base).initialize(database_arguments, recreate=False)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield engine


@pytest.fixture(scope="function")
def session(engine):
    database_connection = engine.connect()
    transaction = database_connection.begin()

    Session = sessionmaker(bind=database_connection)
    session = Session()

    yield session

    session.close()
    if database_connection.in_transaction():
        transaction.rollback()

    database_connection.close()


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
