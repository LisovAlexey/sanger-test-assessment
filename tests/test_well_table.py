import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database

from init_db import EngineCreator, Base, Sample, Well


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

        self.test_sample = Sample(customer_sample_name = "Test sample", tube_barcode = "NT00001")
        self.test_sample_two = Sample(customer_sample_name="Test sample", tube_barcode="NT00002")

        self.session.add(self.test_sample)
        self.session.add(self.test_sample_two)
        self.session.commit()

    def teardown_method(self):
        self.session.close()
        self.transaction.rollback()
        self.connection.close()

    def test_creating_well(self):

        assert self.test_sample.id != None
        print(self.test_sample.id)
        new_well = Well(plate_barcode="DN00001", row=1, col=1, sample_id=self.test_sample.id)
        self.session.add(new_well)
        self.session.commit()

        new_sample_fetched = self.session.query(Well).filter_by(row=1, col=1, plate_barcode="DN00001").first()
        assert new_sample_fetched.row == 1
        assert new_sample_fetched.col == 1
        assert new_sample_fetched.plate_barcode == "DN00001"
        assert new_sample_fetched.sample_id == self.test_sample.id

    def test_creating_well_row_less_than_one(self):
        new_well = Well(plate_barcode="DN00001", row=0, col=1, sample_id=self.test_sample.id)
        self.session.add(new_well)

        with pytest.raises(IntegrityError):
            self.session.commit()

    def test_creating_well_row_more_than_eight(self):
        new_well = Well(plate_barcode="DN00001", row=9, col=1, sample_id=self.test_sample.id)
        self.session.add(new_well)

        with pytest.raises(IntegrityError):
            self.session.commit()

    def test_creating_well_row_eight(self):
        new_well = Well(plate_barcode="DN00001", row=8, col=1, sample_id=self.test_sample.id)
        self.session.add(new_well)
        self.session.commit()

    def test_creating_well_col_less_than_one(self):
        new_well = Well(plate_barcode="DN00001", row=1, col=0, sample_id=self.test_sample.id)
        self.session.add(new_well)
        with pytest.raises(IntegrityError):
            self.session.commit()

    def test_creating_well_col_more_than_twelve(self):
        new_well = Well(plate_barcode="DN00001", row=1, col=13, sample_id=self.test_sample.id)
        self.session.add(new_well)
        with pytest.raises(IntegrityError):
            self.session.commit()

    def test_adding_several_samples_in_one_well(self):
        new_well = Well(plate_barcode="DN00001", row=1, col=1, sample_id=self.test_sample.id)
        self.session.add(new_well)

        new_well = Well(plate_barcode="DN00001", row=1, col=1, sample_id=self.test_sample_two.id)
        self.session.add(new_well)

        with pytest.raises(IntegrityError):
            self.session.commit()

    def test_adding_several_samples_in_one_plate_different_wells(self):
        new_well = Well(plate_barcode="DN00001", row=1, col=1, sample_id=self.test_sample.id)
        self.session.add(new_well)

        new_well = Well(plate_barcode="DN00001", row=1, col=2, sample_id=self.test_sample_two.id)
        self.session.add(new_well)

        self.session.commit()

    def test_row_missing(self):
        new_well = Well(plate_barcode="DN00001", col=1, sample_id=self.test_sample.id)
        self.session.add(new_well)
        with pytest.raises(IntegrityError):
            self.session.commit()

    def test_col_missing(self):
        new_well = Well(plate_barcode="DN00001", row=1, sample_id=self.test_sample.id)
        self.session.add(new_well)
        with pytest.raises(IntegrityError):
            self.session.commit()

    def test_plate_barcode_missing(self):
        new_well = Well(col=1, row=1, sample_id=self.test_sample.id)
        self.session.add(new_well)
        with pytest.raises(IntegrityError):
            self.session.commit()

    def test_sample_id_missing(self):
        new_well = Well(plate_barcode="DN00001", row=1, col=1)
        self.session.add(new_well)
        with pytest.raises(IntegrityError):
            self.session.commit()




