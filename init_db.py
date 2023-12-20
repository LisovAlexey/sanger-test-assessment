from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String, CheckConstraint, ForeignKey, create_engine
from sqlalchemy_utils import database_exists, create_database

Base = declarative_base()

class Sample(Base):
    __tablename__ = 'samples'
    __table_args__ = (
        CheckConstraint('id > 0'),
    )

    id = Column(Integer, primary_key=True)
    customer_sample_name = Column(String)
    tube_barcode = Column(String)


class Well(Base):
    __tablename__ = 'wells'

    plate_barcode = Column(String, primary_key=True)
    row = Column(Integer, primary_key=True)
    column = Column(Integer, primary_key=True)
    sample_id = Column(Integer, ForeignKey("samples.id"))



engine = create_engine('postgresql+psycopg2://user:secret@127.0.0.1:5432/samples')

if not database_exists(engine.url):
    create_database(engine.url)


Session = sessionmaker(bind=engine)
session = Session()

Base.metadata.create_all(engine)