from sqlalchemy import CheckConstraint, Column, Integer, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Sample(Base):
    __tablename__ = 'samples'
    __table_args__ = (
        CheckConstraint('id > 0'),
    )

    id = mapped_column(Integer, primary_key=True)
    customer_sample_name = mapped_column(String)
    tube_barcode = mapped_column(String, unique=True, nullable=False)


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

    plate_barcode = mapped_column(String, primary_key=True, nullable=False)
    row = mapped_column(Integer, primary_key=True, nullable=False)
    col = mapped_column(Integer, primary_key=True, nullable=False)
    sample_id = mapped_column(Integer, ForeignKey("samples.id"), nullable=False)
