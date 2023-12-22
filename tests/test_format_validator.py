import pytest
from format_validator import tube_barcode_validator, plate_barcode_validator

class TestFormatValidator:

    def test_tube_barcode_validator(self):
        assert tube_barcode_validator.validate("NT1")
        assert tube_barcode_validator.validate("NT10000")
        assert tube_barcode_validator.validate("NT00001")

    def test_tube_barcode_validator_wrong_letters(self):
        assert not tube_barcode_validator.validate("HZ1")

    def test_tube_barcode_validator_no_letter_id(self):
        assert not tube_barcode_validator.validate("1")

    def test_tube_barcode_validator_no_number_id(self):
        assert not tube_barcode_validator.validate("NT")

    def test_plate_barcode_validator(self):
        assert plate_barcode_validator.validate("DN1")
        assert plate_barcode_validator.validate("DN10000")
        assert plate_barcode_validator.validate("DN00001")

    def test_plate_barcode_validator_no_number_id(self):
        assert not tube_barcode_validator.validate("DN")
