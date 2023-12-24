from sqlalchemy import CheckConstraint, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base

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
