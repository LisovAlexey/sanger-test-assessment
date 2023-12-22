import pytest
from sqlalchemy.exc import IntegrityError
from fixtures import session, database_connection, engine

from init_db import EngineCreator, Base, Well, Sample


class TestSampleTable:

    def test_creating_well(self, session):
        new_sample = Sample(id=1, customer_sample_name="test", tube_barcode="NT00001")
        session.add(new_sample)
        session.commit()

        new_sample_fetched = session.query(Sample).filter_by(id=1).first()
        assert new_sample_fetched.id == 1
        assert new_sample_fetched.customer_sample_name == "test"
        assert new_sample_fetched.tube_barcode == "NT00001"

    def test_creating_sample_dublicate(self, session):
        new_sample = Sample(id=1, customer_sample_name="test", tube_barcode="NT00001")
        session.add(new_sample)
        session.commit()

        new_sample2 = Sample(id=1, customer_sample_name="test", tube_barcode="NT00001")
        session.add(new_sample2)

        with pytest.raises(IntegrityError):
            session.commit()

    def test_creating_tube_barcode_dublicate(self, session):
        new_sample = Sample(customer_sample_name="test", tube_barcode="NT00001")
        session.add(new_sample)
        session.commit()

        new_sample2 = Sample(customer_sample_name="test2", tube_barcode="NT00001")
        session.add(new_sample2)

        with pytest.raises(IntegrityError):
            session.commit()

    def test_creating_customer_sample_name_dublicate(self, session):
        new_sample = Sample(customer_sample_name="test", tube_barcode="NT00001")
        session.add(new_sample)
        session.commit()

        new_sample2 = Sample(customer_sample_name="test", tube_barcode="NT00002")
        session.add(new_sample2)
        session.commit()

    def test_tube_barcode_missing(self, session):
        new_sample = Sample(customer_sample_name="test")
        session.add(new_sample)
        with pytest.raises(IntegrityError):
            session.commit()

    def test_autoincrease_id(self, session):
        new_sample = Sample(customer_sample_name="test", tube_barcode="NT00001")
        session.add(new_sample)
        session.commit()

        new_sample2 = Sample(customer_sample_name="test", tube_barcode="NT00002")
        session.add(new_sample2)
        session.commit()

        assert (new_sample.id + 1) == new_sample2.id
        assert new_sample.id > 0
        assert new_sample2.id > 0


