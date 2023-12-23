import pytest


@pytest.fixture(scope="function")
def sample_one(database_layer):
    # The database_layer does not need to be rolled back because sessions are already rolled back
    yield database_layer.record_receipt(customer_sample_name="test", tube_barcode="NT123")


@pytest.fixture(scope="function")
def sample_two(database_layer):
    yield database_layer.record_receipt(customer_sample_name="test second sample", tube_barcode="NT333")
