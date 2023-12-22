import pytest
from database import BadFunctionSignature, BadBarcodeFormat, SampleAlreadyReceived, DatabaseLayer
from fixtures import database_connection, engine, database_layer




class TestRecordReceipt:
    def test_record_receipt(self, database_layer):
        database_layer.record_receipt(customer_sample_name="test_tube", tube_barcode="NT00001")

    def test_record_receipt_with_non_string_object(self, database_layer):
        # Any str convertable objects can be passed in function
        database_layer.record_receipt(customer_sample_name=123, tube_barcode="NT00001")
    def test_record_receipt_with_non_string_object_any_number_format(self, database_layer):
        # Any str convertable objects can be passed in function
        database_layer.record_receipt(customer_sample_name=123, tube_barcode="NT1")

    def test_record_receipt_with_wrong_tube_barcode_format_letters(self, database_layer):
        # Any str convertable objects can be passed in function
        with pytest.raises(BadBarcodeFormat):
            database_layer.record_receipt(customer_sample_name="test_tube", tube_barcode="NTABC")

    def test_record_receipt_with_wrong_tube_barcode_format_no_number(self, database_layer):
        # Any str convertable objects can be passed in function
        with pytest.raises(BadBarcodeFormat):
            database_layer.record_receipt(customer_sample_name="test_tube", tube_barcode="NT")

    def test_record_receipt_with_wrong_tube_barcode_format_first_number(self, database_layer):
        # Any str convertable objects can be passed in function
        with pytest.raises(BadBarcodeFormat):
            database_layer.record_receipt(customer_sample_name="test_tube", tube_barcode="123NT")


    def test_record_receipt_dublicate_tubes(self, database_layer):
        # Any str convertable objects can be passed in function
        database_layer.record_receipt(customer_sample_name="test_tube", tube_barcode="NT1")

        with pytest.raises(SampleAlreadyReceived):
            database_layer.record_receipt(customer_sample_name="test_tube", tube_barcode="NT1")

