import pytest
import typing as tp
from dotenv import load_dotenv
from sqlalchemy import Engine
from sqlalchemy.orm import sessionmaker, Session

from database.database import DatabaseLayer
from database.management import DatabaseInitializer
from database.scheme import Base, Sample
from env import read_database_credentials_from_env


@pytest.fixture(scope="module")
def engine() -> tp.Generator[Engine, None, None]:
    load_dotenv()
    database_arguments = read_database_credentials_from_env("TEST")

    engine = DatabaseInitializer(Base=Base).init_database(database_arguments, recreate=False)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield engine


@pytest.fixture(scope="function")
def session(engine: Engine) -> tp.Generator[Session, None, None]:
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
def database_layer(session: Session) -> tp.Generator[DatabaseLayer, None, None]:
    yield DatabaseLayer(session)


@pytest.fixture(scope="function")
def sample_one(database_layer: DatabaseLayer) -> tp.Generator[Sample, None, None]:
    # The database_layer does not need to be rolled back because sessions are already rolled back
    yield database_layer.record_receipt(customer_sample_name="test", tube_barcode="NT123")


@pytest.fixture(scope="function")
def sample_two(database_layer: DatabaseLayer) -> tp.Generator[Sample, None, None]:
    yield database_layer.record_receipt(customer_sample_name="test second sample", tube_barcode="NT333")
