import pytest
from add_to_plate import add_to_plate, WellPositionBadFormatting, WellPositionOccupied, SampleNotFound, \
    SampleIdBadFormatting
from record_receipt import record_receipt


class TestAddToPlate:

    # create samples for each test

    def setup_class(self):
        self.sample_id = record_receipt(customer_sample_name="test", tube_barcode="NT123")
        self.sample_id_two = record_receipt(customer_sample_name="test second sample", tube_barcode="NT333")

    def test_add_to_plate(self):
        add_to_plate(sample_id=self.sample_id, plate_barcode="DN1", well_position="A1")

    def test_well_position_format_number_only(self):
        with pytest.raises(WellPositionBadFormatting):
            add_to_plate(sample_id=self.sample_id, plate_barcode="DN1", well_position="1")

    def test_well_position_format_char_only(self):
        with pytest.raises(WellPositionBadFormatting):
            add_to_plate(sample_id=self.sample_id, plate_barcode="DN1", well_position="A")

    def test_well_position_out_of_bounds_column(self):
        with pytest.raises(WellPositionBadFormatting):
            add_to_plate(sample_id=self.sample_id, plate_barcode="DN1", well_position="A13")

    def test_well_position_out_of_bounds_row(self):
        with pytest.raises(WellPositionBadFormatting):
            add_to_plate(sample_id=self.sample_id, plate_barcode="DN1", well_position="Z1")

    def test_well_position_out_of_bounds_mixed(self):
        with pytest.raises(WellPositionBadFormatting):
            add_to_plate(sample_id=self.sample_id, plate_barcode="DN1", well_position="Z100")

    def test_plate_barcode_invalid_format_underscore(self):
        with pytest.raises(WellPositionBadFormatting):
            add_to_plate(sample_id=self.sample_id, plate_barcode="DN_1", well_position="A1")

    def test_plate_barcode_invalid_format_missing_number(self):
        with pytest.raises(WellPositionBadFormatting):
            add_to_plate(sample_id=self.sample_id, plate_barcode="DN", well_position="A1")

    def test_plate_barcode_invalid_format_prefix(self):
        with pytest.raises(WellPositionBadFormatting):
            add_to_plate(sample_id=self.sample_id, plate_barcode="PR1", well_position="A1")

    def test_plate_barcode_invalid_format_number_prefix(self):
        with pytest.raises(WellPositionBadFormatting):
            add_to_plate(sample_id=self.sample_id, plate_barcode="1DN", well_position="A1")

    def test_plate_adding_samples_to_several_wells(self):
        add_to_plate(sample_id=self.sample_id, plate_barcode="DN1", well_position="A1")
        add_to_plate(sample_id=self.sample_id, plate_barcode="DN1", well_position="A2")
        add_to_plate(sample_id=self.sample_id, plate_barcode="DN1", well_position="B2")
        add_to_plate(sample_id=self.sample_id, plate_barcode="DN1", well_position="B3")

    def test_well_position_occupied(self):
        add_to_plate(sample_id=self.sample_id, plate_barcode="DN1", well_position="A1")

        with pytest.raises(WellPositionOccupied):
            add_to_plate(sample_id=self.sample_id, plate_barcode="DN1", well_position="A1")

    def test_well_position_occupied_different_samples(self):
        add_to_plate(sample_id=self.sample_id, plate_barcode="DN1", well_position="A1")

        with pytest.raises(WellPositionOccupied):
            add_to_plate(sample_id=self.sample_id_two, plate_barcode="DN1", well_position="A1")

    def test_well_sample_not_found(self):
        with pytest.raises(SampleNotFound):
            add_to_plate(sample_id=993, plate_barcode="DN1", well_position="A1")

    def test_sample_id_wrong_format(self):
        with pytest.raises(SampleIdBadFormatting):
            add_to_plate(sample_id=-1, plate_barcode="DN1", well_position="A1")

