from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String, CheckConstraint, ForeignKey, create_engine, Engine
from sqlalchemy_utils import database_exists, create_database

import typing as tp
Base = declarative_base()

class Sample(Base):
    __tablename__ = 'samples'
    __table_args__ = (
        CheckConstraint('id > 0'),
    )

    id = Column(Integer, primary_key=True)
    customer_sample_name = Column(String)
    tube_barcode = Column(String, unique=True, nullable=False)


class Well(Base):
    """
    plate_barcode: DN00001...
    """
    __tablename__ = 'wells'
    __table_args__ = (
        CheckConstraint('row >= 1'),
        CheckConstraint('row <= 8'),

        CheckConstraint('col >= 1'),
        CheckConstraint('col <= 12'),
    )

    plate_barcode = Column(String, primary_key=True, nullable=False)
    row = Column(Integer, primary_key=True, nullable=False)
    col = Column(Integer, primary_key=True, nullable=False)
    sample_id = Column(Integer, ForeignKey("samples.id"), nullable=False)


class EngineCreator:
    def __init__(self):
        pass

    @staticmethod
    def create_engine(database: str, user: str, password: str, host: str, port: tp.Union[str, int], database_name: str) -> Engine:
        return create_engine(
            f'{database}://{user}:{password}@{host}:{port}/{database_name}')

    @staticmethod
    def create_test_database() -> Engine:
        return EngineCreator.create_engine(
            database="postgresql+psycopg2",
            user="user",
            password="secret",
            host="localhost",
            port = 5432,
            database_name="test_database"
        )

    @staticmethod
    def drop_test_database() -> None:
        engine = EngineCreator.create_test_database()
        Base.metadata.drop_all(bind=engine)


if __name__ == '__main__':
    EngineCreator.drop_test_database()

# engine = create_engine('postgresql+psycopg2://user:secret@127.0.0.1:5432/samples')
#
# if not database_exists(engine.url):
#     create_database(engine.url)
#
#
# Session = sessionmaker(bind=engine)
# session = Session()
#
# Base.metadata.create_all(engine)