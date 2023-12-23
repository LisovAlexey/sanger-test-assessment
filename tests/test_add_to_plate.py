import pytest

from fixtures import database_connection, engine, database_layer, session

from database import SampleIdBadFormatting, SampleNotFound, WellPositionOccupied, PlateBarcodeBadFormat
from reports import WellPositionBadFormatting


@pytest.fixture(scope="function")
def sample_one(database_layer):
    # Do not need to be rolled back because sessions are rollbacked
    yield database_layer.record_receipt(customer_sample_name="test", tube_barcode="NT123")


@pytest.fixture(scope="function")
def sample_two(database_layer):
    yield database_layer.record_receipt(customer_sample_name="test second sample", tube_barcode="NT333")


class TestAddToPlate:

    def test_add_to_plate(self, database_layer, sample_one):
        database_layer.add_to_plate(sample_id=sample_one.id, plate_barcode="DN1", well_position="A1")

    def test_well_position_format_number_only(self, database_layer, sample_one):
        with pytest.raises(WellPositionBadFormatting):
            database_layer.add_to_plate(sample_id=sample_one.id, plate_barcode="DN1", well_position="1")

    def test_well_position_format_char_only(self, database_layer, sample_one):
        with pytest.raises(WellPositionBadFormatting):
            database_layer.add_to_plate(sample_id=sample_one.id, plate_barcode="DN1", well_position="A")

    def test_well_position_out_of_bounds_column(self, database_layer, sample_one):
        with pytest.raises(WellPositionBadFormatting):
            database_layer.add_to_plate(sample_id=sample_one.id, plate_barcode="DN1", well_position="A13")

    def test_well_position_out_of_bounds_row(self, database_layer, sample_one):
        with pytest.raises(WellPositionBadFormatting):
            database_layer.add_to_plate(sample_id=sample_one.id, plate_barcode="DN1", well_position="Z1")

    def test_well_position_out_of_bounds_mixed(self, database_layer, sample_one):
        with pytest.raises(WellPositionBadFormatting):
            database_layer.add_to_plate(sample_id=sample_one.id, plate_barcode="DN1", well_position="Z100")

    def test_plate_barcode_invalid_format_underscore(self, database_layer, sample_one):
        with pytest.raises(PlateBarcodeBadFormat):
            database_layer.add_to_plate(sample_id=sample_one.id, plate_barcode="DN_1", well_position="A1")

    def test_plate_barcode_invalid_format_missing_number(self, database_layer, sample_one):
        with pytest.raises(PlateBarcodeBadFormat):
            database_layer.add_to_plate(sample_id=sample_one.id, plate_barcode="DN", well_position="A1")

    def test_plate_barcode_invalid_format_prefix(self, database_layer, sample_one):
        with pytest.raises(PlateBarcodeBadFormat):
            database_layer.add_to_plate(sample_id=sample_one.id, plate_barcode="PR1", well_position="A1")

    def test_plate_barcode_invalid_format_number_prefix(self, database_layer, sample_one):
        with pytest.raises(PlateBarcodeBadFormat):
            database_layer.add_to_plate(sample_id=sample_one.id, plate_barcode="1DN", well_position="A1")

    def test_plate_adding_samples_to_several_wells(self, database_layer, sample_one):
        database_layer.add_to_plate(sample_id=sample_one.id, plate_barcode="DN1", well_position="A1")
        database_layer.add_to_plate(sample_id=sample_one.id, plate_barcode="DN1", well_position="A2")
        database_layer.add_to_plate(sample_id=sample_one.id, plate_barcode="DN1", well_position="B2")
        database_layer.add_to_plate(sample_id=sample_one.id, plate_barcode="DN1", well_position="B3")

    def test_well_position_occupied(self, database_layer, sample_one):
        database_layer.add_to_plate(sample_id=sample_one.id, plate_barcode="DN1", well_position="A1")

        with pytest.raises(WellPositionOccupied):
            database_layer.add_to_plate(sample_id=sample_one.id, plate_barcode="DN1", well_position="A1")

    def test_well_position_occupied_different_samples(self, database_layer, sample_one, sample_two):
        database_layer.add_to_plate(sample_id=sample_one.id, plate_barcode="DN1", well_position="A1")

        with pytest.raises(WellPositionOccupied):
            database_layer.add_to_plate(sample_id=sample_two.id, plate_barcode="DN1", well_position="A1")

    def test_well_sample_not_found(self, database_layer):
        with pytest.raises(SampleNotFound):
            database_layer.add_to_plate(sample_id=993, plate_barcode="DN1", well_position="A1")

    def test_sample_id_wrong_format(self, database_layer):
        with pytest.raises(SampleIdBadFormatting):
            database_layer.add_to_plate(sample_id=-1, plate_barcode="DN1", well_position="A1")
