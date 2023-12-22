import pytest

from database import TubeBarcodeBadFormat, TubeReport, PlateReport, DatabaseLayer, \
    TubeNotFound, OccupiedWellsNotFound, BarcodeBadFormat
from fixtures import database_layer, session, engine, database_connection
from test_add_to_plate import sample_one, sample_two


@pytest.fixture(scope="module")
def plate_barcode():
    yield "DN1"
@pytest.fixture(scope="function")
def well_one(sample_one, plate_barcode, database_layer):
    yield database_layer.add_to_plate(sample_id=sample_one.id,
                       plate_barcode=plate_barcode,
                       well_position="A1")

@pytest.fixture(scope="function")
def well_two(sample_one, plate_barcode, database_layer):
    yield database_layer.add_to_plate(sample_id=sample_one.id,
                       plate_barcode=plate_barcode,
                       well_position="A2")

@pytest.fixture(scope="function")
def well_three(sample_one, plate_barcode, database_layer):
    yield database_layer.add_to_plate(sample_id=sample_one.id,
                       plate_barcode=plate_barcode,
                       well_position="B2")

@pytest.fixture(scope="function")
def wells(well_one, well_two, well_three):
    yield [well_one, well_two, well_three]

class TestListSamplesIn:

    def test_list_samples_in_tube(self, database_layer, sample_one, wells):
        tube_report = database_layer.list_samples_in(container_barcode=sample_one.tube_barcode)

        assert isinstance(tube_report, TubeReport)
        assert tube_report.barcode == sample_one.tube_barcode
        assert tube_report.sample_id == sample_one.id
        assert tube_report.customer_sample_name == sample_one.customer_sample_name

    def test_list_samples_in_plate(self, database_layer, plate_barcode, wells):
        plate_report = database_layer.list_samples_in(container_barcode=plate_barcode)

        assert isinstance(plate_report, PlateReport)
        assert plate_report.barcode == plate_barcode
        assert set(plate_report.wells) == set(wells)

    def test_list_samples_in_tube_not_found(self, database_layer):
        with pytest.raises(TubeNotFound):
            database_layer.list_samples_in(container_barcode="NT9999")

    def test_list_samples_in_plate_not_found(self, database_layer):
        with pytest.raises(OccupiedWellsNotFound):
            database_layer.list_samples_in(container_barcode="DN9999")

    def test_list_samples_in_bad_barcode_format(self, database_layer):
        with pytest.raises(BarcodeBadFormat):
            database_layer.list_samples_in(container_barcode="9999")
