import cmd2_ext_test
import pytest
from sqlalchemy.orm import sessionmaker

from database.database import DatabaseLayer
from main import MyCLIApp, DatabaseInitializer
from cmd2 import CommandResult


class DefaultAppTester(cmd2_ext_test.ExternalTestMixin, MyCLIApp):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


@pytest.fixture(scope="function")
def default_app(database_layer):
    app = DefaultAppTester(database_layer=database_layer)
    app.fixture_setup()
    yield app
    app.fixture_teardown()


class TestRecordReceiptCLIInterface:

    def test_record_receipt(self, default_app):
        out = default_app.app_cmd("record_receipt 'Test sample' NT100")

        assert isinstance(out, CommandResult)
        assert str(out.stderr) == ""
        assert str(out.stdout).strip() == 'Successfully recorded receipt: Test sample [NT100]'

    def test_record_receipt_bad_barcode_format(self, default_app):
        out = default_app.app_cmd("record_receipt 'Test sample' wrong_format")

        assert isinstance(out, CommandResult)
        assert str(out.stderr) == ""
        assert str(out.stdout).strip() == 'Bad barcode: wrong_format. Expected NT<Number>'

    def test_record_receipt_duplicate(self, default_app):
        out = default_app.app_cmd("record_receipt 'Test sample' NT100")

        out = default_app.app_cmd("record_receipt 'Test sample the same' NT100")

        assert isinstance(out, CommandResult)
        assert str(out.stderr) == ""
        assert str(out.stdout).strip() == f'Sample in tube [NT100] was already received.'


class TestAddToPlateCLIInterface:

    def test_add_to_plate(self, default_app):
        sample = default_app.database_layer.record_receipt("Test sample", "NT1")

        out = default_app.app_cmd(f"add_to_plate {sample.id} DN100 A1")

        assert isinstance(out, CommandResult)
        assert str(out.stderr) == ""
        assert str(out.stdout).strip() == f'Successfully added sample (id: {sample.id}) to plate DN100 at A1'

    def test_add_to_plate_bad_sample_id(self, default_app):
        sample = default_app.database_layer.record_receipt("Test sample", "NT1")

        out = default_app.app_cmd(f"add_to_plate {-2} DN100 A1")

        assert isinstance(out, CommandResult)
        assert str(out.stderr) == ""
        assert str(out.stdout).strip() == f"Bad sample id: -2. Expected NT<PositiveNumber>"

    def test_add_to_plate_well_position_bad_format(self, default_app):
        sample = default_app.database_layer.record_receipt("Test sample", "NT1")

        out = default_app.app_cmd(f"add_to_plate {sample.id} DN100 some_well")

        assert isinstance(out, CommandResult)
        assert str(out.stderr) == ""
        assert str(
            out.stdout).strip() == f'Well position wrong format. Expected: "<Letter [A-H]><Number [1-12]>". Got: some_well'

    def test_add_to_plate_no_such_sample(self, default_app):
        sample = default_app.database_layer.record_receipt("Test sample", "NT1")

        missing_sample_id = 99999999
        assert sample.id != missing_sample_id

        out = default_app.app_cmd(f"add_to_plate {missing_sample_id} DN100 A1")

        assert isinstance(out, CommandResult)
        assert str(out.stderr) == ""
        assert str(out.stdout).strip() == f"Sample (id: {missing_sample_id}) not found in table."

    def test_add_to_plate_well_position_occupied(self, default_app):
        sample = default_app.database_layer.record_receipt("Test sample", "NT1")
        default_app.app_cmd(f"add_to_plate {sample.id} DN100 A1")

        out = default_app.app_cmd(f"add_to_plate {sample.id} DN100 A1")

        assert isinstance(out, CommandResult)
        assert str(out.stderr) == ""
        assert str(out.stdout).strip() == f"Well at position A1 already occupied."


class TestTubeTransferCLIInterface:

    def test_tube_transfer(self, default_app):
        _ = default_app.database_layer.record_receipt("Test sample", "NT1")

        out = default_app.app_cmd(f"tube_transfer NT1 NT2")

        assert isinstance(out, CommandResult)
        assert str(out.stderr) == ""
        assert str(out.stdout).strip() == f"Successfully transfer sample from tube (NT1) " + \
               f"to tube (NT2)"

    def test_tube_transfer_barcode_format(self, default_app):
        out = default_app.app_cmd(f"tube_transfer some_barcode1 some_barcode2")

        assert isinstance(out, CommandResult)
        assert str(out.stderr) == ""
        assert str(out.stdout).strip() == f"Bad tube barcode format: some_barcode1 / some_barcode2. " + \
               f"Should be: NT<Number>"

    def test_tube_transfer_destination_tube_occupied(self, default_app):
        _ = default_app.database_layer.record_receipt("Test sample", "NT1")
        _ = default_app.database_layer.record_receipt("Test sample 2", "NT2")

        out = default_app.app_cmd(f"tube_transfer NT1 NT2")

        assert isinstance(out, CommandResult)
        assert str(out.stderr) == ""
        assert str(out.stdout).strip() == f"Destination tube (NT2) is already occupied."

    def test_tube_transfer_source_tube_empty(self, default_app):
        out = default_app.app_cmd(f"tube_transfer NT1 NT2")

        assert isinstance(out, CommandResult)
        assert str(out.stderr) == ""
        assert str(out.stdout).strip() == f'Source tube (NT1) is empty.'
