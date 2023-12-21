import pytest
from record_receipt import record_receipt, BadFunctionSignature, BadBarcodeFormat, SampleAlreadyReceived


class TestRecordReceipt:
    def test_record_receipt(self):
        record_receipt(customer_sample_name="test_tube", tube_barcode="NT00001")

    def test_record_receipt_with_non_string_object(self):
        # Any str convertable objects can be passed in function
        record_receipt(customer_sample_name=123, tube_barcode="NT00001")
    def test_record_receipt_with_non_string_object_any_number_format(self):
        # Any str convertable objects can be passed in function
        record_receipt(customer_sample_name=123, tube_barcode="NT1")

    def test_record_receipt_with_wrong_tube_barcode_format_letters(self):
        # Any str convertable objects can be passed in function
        with pytest.raises(BadBarcodeFormat):
            record_receipt(customer_sample_name="test_tube", tube_barcode="NTABC")

    def test_record_receipt_with_wrong_tube_barcode_format_no_number(self):
        # Any str convertable objects can be passed in function
        with pytest.raises(BadBarcodeFormat):
            record_receipt(customer_sample_name="test_tube", tube_barcode="NT")

    def test_record_receipt_with_wrong_tube_barcode_format_first_number(self):
        # Any str convertable objects can be passed in function
        with pytest.raises(BadBarcodeFormat):
            record_receipt(customer_sample_name="test_tube", tube_barcode="123NT")


    def test_record_receipt_dublicate_tubes(self):
        # Any str convertable objects can be passed in function
        record_receipt(customer_sample_name="test_tube", tube_barcode="NT1")

        with pytest.raises(SampleAlreadyReceived):
            record_receipt(customer_sample_name="test_tube", tube_barcode="NT1")

