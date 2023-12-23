import pytest
from sqlalchemy.exc import IntegrityError
from tests.fixtures import session, database_connection, engine

from init_db import Sample


class TestSampleTable:

    def test_creating_well(self, session):
        new_sample = Sample(id=1, customer_sample_name="test", tube_barcode="NT00001")
        session.add(new_sample)
        session.commit()

        new_sample_fetched = session.query(Sample).filter_by(id=1).first()
        assert new_sample_fetched.id == 1
        assert new_sample_fetched.customer_sample_name == "test"
        assert new_sample_fetched.tube_barcode == "NT00001"

    def test_creating_sample_duplicate(self, session):
        new_sample = Sample(id=1, customer_sample_name="test", tube_barcode="NT00001")
        session.add(new_sample)
        session.commit()

        new_sample2 = Sample(id=1, customer_sample_name="test", tube_barcode="NT00001")
        session.add(new_sample2)

        with pytest.raises(IntegrityError):
            session.commit()

    def test_creating_tube_barcode_duplicate(self, session):
        new_sample = Sample(customer_sample_name="test", tube_barcode="NT00001")
        session.add(new_sample)
        session.commit()

        new_sample2 = Sample(customer_sample_name="test2", tube_barcode="NT00001")
        session.add(new_sample2)

        with pytest.raises(IntegrityError):
            session.commit()

    def test_creating_customer_sample_name_duplicate(self, session):
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

    def test_auto_increase_id(self, session):
        new_sample = Sample(customer_sample_name="test", tube_barcode="NT00001")
        session.add(new_sample)
        session.commit()

        new_sample2 = Sample(customer_sample_name="test", tube_barcode="NT00002")
        session.add(new_sample2)
        session.commit()

        assert (new_sample.id + 1) == new_sample2.id
        assert new_sample.id > 0
        assert new_sample2.id > 0

    def test_search_object_by_id(self, session):
        new_sample = Sample(id=1, customer_sample_name="test", tube_barcode="NT00001")
        session.add(new_sample)
        session.commit()

        query = session.query(Sample.id).filter(Sample.id == 1)
        assert session.query(query.exists()).scalar()

        query = session.query(Sample.id).filter(Sample.id == 2)
        assert not session.query(query.exists()).scalar()

    def test_search_object_by_tube_barcode(self, session):
        new_sample = Sample(id=1, customer_sample_name="test", tube_barcode="NT00001")
        session.add(new_sample)
        session.commit()

        fetched_sample = session.query(Sample).filter(Sample.tube_barcode == "NT00001").first()
        assert fetched_sample.id == 1
        assert fetched_sample.customer_sample_name == "test"
        assert fetched_sample.tube_barcode == "NT00001"

    def test_search_missing_object_by_tube_barcode(self, session):
        new_sample = Sample(id=1, customer_sample_name="test", tube_barcode="NT00001")
        session.add(new_sample)
        session.commit()

        fetched_sample = session.query(Sample).filter(Sample.tube_barcode == "NT99999").first()
        assert fetched_sample is None
