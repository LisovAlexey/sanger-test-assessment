import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database

from init_db import EngineCreator, Base, Well, Sample


class TestWellTable:
    def setup_class(self):
        engine = EngineCreator.create_test_database()
        if not database_exists(engine.url):
            create_database(engine.url)
        Base.metadata.create_all(engine)

        self.engine = engine


    def setup_method(self, method):
        # self.engine = engine
        self.connection = self.engine.connect()
        self.transaction = self.connection.begin()

        Session = sessionmaker(bind=self.connection)
        self.session = Session()
    def teardown_method(self):
        self.session.close()
        self.transaction.rollback()
        self.connection.close()

    def test_creating_well(self):
        new_sample = Sample(id=1, customer_sample_name="test", tube_barcode="NT00001")
        self.session.add(new_sample)
        self.session.commit()

        new_sample_fetched = self.session.query(Sample).filter_by(id=1).first()
        assert new_sample_fetched.id == 1
        assert new_sample_fetched.customer_sample_name == "test"
        assert new_sample_fetched.tube_barcode == "NT00001"

    def test_creating_sample_dublicate(self):
        new_sample = Sample(id=1, customer_sample_name="test", tube_barcode="NT00001")
        self.session.add(new_sample)
        self.session.commit()

        new_sample2 = Sample(id=1, customer_sample_name="test", tube_barcode="NT00001")
        self.session.add(new_sample2)

        with pytest.raises(IntegrityError):
            self.session.commit()

    def test_creating_tube_barcode_dublicate(self):
        new_sample = Sample(customer_sample_name="test", tube_barcode="NT00001")
        self.session.add(new_sample)
        self.session.commit()

        new_sample2 = Sample(customer_sample_name="test2", tube_barcode="NT00001")
        self.session.add(new_sample2)

        with pytest.raises(IntegrityError):
            self.session.commit()

    def test_creating_customer_sample_name_dublicate(self):
        new_sample = Sample(customer_sample_name="test", tube_barcode="NT00001")
        self.session.add(new_sample)
        self.session.commit()

        new_sample2 = Sample(customer_sample_name="test", tube_barcode="NT00002")
        self.session.add(new_sample2)
        self.session.commit()

    def test_tube_barcode_missing(self):
        new_sample = Sample(customer_sample_name="test")
        self.session.add(new_sample)
        with pytest.raises(IntegrityError):
            self.session.commit()

    def test_autoincrease_id(self):
        new_sample = Sample(customer_sample_name="test", tube_barcode="NT00001")
        self.session.add(new_sample)
        self.session.commit()

        new_sample2 = Sample(customer_sample_name="test", tube_barcode="NT00002")
        self.session.add(new_sample2)
        self.session.commit()

        assert (new_sample.id + 1) == new_sample2.id
        assert new_sample.id > 0
        assert new_sample2.id > 0


