import pytest
from sqlalchemy.exc import IntegrityError
from fixtures import session, database_connection, engine, database_layer

from init_db import Sample, Well
from tests.test_add_to_plate import sample_one, sample_two


class TestWellTable:

    def test_creating_well(self, session, sample_one):
        assert sample_one.id != None
        new_well = Well(plate_barcode="DN00001", row=1, col=1, sample_id=sample_one.id)
        session.add(new_well)
        session.commit()

        new_sample_fetched = session.query(Well).filter_by(row=1, col=1, plate_barcode="DN00001").first()
        assert new_sample_fetched.row == 1
        assert new_sample_fetched.col == 1
        assert new_sample_fetched.plate_barcode == "DN00001"
        assert new_sample_fetched.sample_id == sample_one.id

    def test_creating_well_row_less_than_one(self, session, sample_one):
        new_well = Well(plate_barcode="DN00001", row=0, col=1, sample_id=sample_one.id)
        session.add(new_well)

        with pytest.raises(IntegrityError):
            session.commit()

    def test_creating_well_row_more_than_eight(self, session, sample_one):
        new_well = Well(plate_barcode="DN00001", row=9, col=1, sample_id=sample_one.id)
        session.add(new_well)

        with pytest.raises(IntegrityError):
            session.commit()

    def test_creating_well_row_eight(self, session, sample_one):
        new_well = Well(plate_barcode="DN00001", row=8, col=1, sample_id=sample_one.id)
        session.add(new_well)
        session.commit()

    def test_creating_well_col_less_than_one(self, session, sample_one):
        new_well = Well(plate_barcode="DN00001", row=1, col=0, sample_id=sample_one.id)
        session.add(new_well)
        with pytest.raises(IntegrityError):
            session.commit()

    def test_creating_well_col_more_than_twelve(self, session, sample_one):
        new_well = Well(plate_barcode="DN00001", row=1, col=13, sample_id=sample_one.id)
        session.add(new_well)
        with pytest.raises(IntegrityError):
            session.commit()

    def test_adding_several_samples_in_one_well(self, session, sample_one, sample_two):
        new_well = Well(plate_barcode="DN00001", row=1, col=1, sample_id=sample_one.id)
        session.add(new_well)

        new_well = Well(plate_barcode="DN00001", row=1, col=1, sample_id=sample_two.id)
        session.add(new_well)

        with pytest.raises(IntegrityError):
            session.commit()

    def test_adding_several_samples_in_one_plate_different_wells(self, session, sample_one, sample_two):
        new_well = Well(plate_barcode="DN00001", row=1, col=1, sample_id=sample_one.id)
        session.add(new_well)

        new_well = Well(plate_barcode="DN00001", row=1, col=2, sample_id=sample_two.id)
        session.add(new_well)

        session.commit()

    def test_row_missing(self, session, sample_one):
        new_well = Well(plate_barcode="DN00001", col=1, sample_id=sample_one.id)
        session.add(new_well)
        with pytest.raises(IntegrityError):
            session.commit()

    def test_col_missing(self, session, sample_one):
        new_well = Well(plate_barcode="DN00001", row=1, sample_id=sample_one.id)
        session.add(new_well)
        with pytest.raises(IntegrityError):
            session.commit()

    def test_plate_barcode_missing(self, session, sample_one):
        new_well = Well(col=1, row=1, sample_id=sample_one.id)
        session.add(new_well)
        with pytest.raises(IntegrityError):
            session.commit()

    def test_sample_id_missing(self, session, sample_one):
        new_well = Well(plate_barcode="DN00001", row=1, col=1)
        session.add(new_well)
        with pytest.raises(IntegrityError):
            session.commit()

    def test_joining_well_and_sample_table(self, session, sample_one):
        new_well = Well(plate_barcode="DN00001", row=8, col=1, sample_id=sample_one.id)
        session.add(new_well)
        session.commit()

        fetched_wells_and_samples = session.query(Well, Sample) \
            .join(Well, Sample.id == Well.sample_id) \
            .filter(Well.plate_barcode == "DN00001") \
            .all()

        assert fetched_wells_and_samples == [(new_well, sample_one)]
