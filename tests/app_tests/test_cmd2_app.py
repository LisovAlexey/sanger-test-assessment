import cmd2_ext_test
import pytest
from sqlalchemy.orm import sessionmaker

from database.database import DatabaseLayer
from main import MyCLIApp, DatabaseInitializer
from cmd2 import CommandResult


class DefaultAppTester(cmd2_ext_test.ExternalTestMixin, MyCLIApp):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


@pytest.fixture
def default_app():

    # Alternatively we can mock DatabaseLayer
    db_initializer = DatabaseInitializer()
    engine = db_initializer.initalize(recreate=True)

    connection = engine.connect()

    Session = sessionmaker(bind=connection)
    session = Session()

    app = DefaultAppTester(database_layer=DatabaseLayer(session))
    app.fixture_setup()
    yield app
    app.fixture_teardown()


class TestRecordReceiptCLIInterface:

    def test_record_receipt(self, default_app):
        # execute a command
        out = default_app.app_cmd("record_receipt 'Test sample' NT100")

        # validate the command output and result data
        assert isinstance(out, CommandResult)
        assert str(out.stderr) == ""
        assert str(out.stdout).strip() == 'Successfully recorded receipt: Test sample [NT100]'

    def test_record_receipt_bad_barcode_format(self, default_app):
        # execute a command
        out = default_app.app_cmd("record_receipt 'Test sample' wrong_format")

        # validate the command output and result data
        assert isinstance(out, CommandResult)
        assert str(out.stderr) == ""
        assert str(out.stdout).strip() == 'Bad barcode: wrong_format. Expected NT<Number>'

    def test_record_receipt_duplicate(self, default_app):
        # execute a command
        out = default_app.app_cmd("record_receipt 'Test sample' NT100")

        out = default_app.app_cmd("record_receipt 'Test sample the same' NT100")

        # validate the command output and result data
        assert isinstance(out, CommandResult)
        assert str(out.stderr) == ""
        assert str(out.stdout).strip() == f'Sample in tube [NT100] was already received.'
