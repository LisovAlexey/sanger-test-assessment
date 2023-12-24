# This is a sample Python script.
import typing as tp
import argparse
import cmd2
from sqlalchemy import Engine

from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database

from database.database import DatabaseLayer
from env import force_get_env_var
from exceptions import TubeBarcodeBadFormat, SampleAlreadyReceived, SampleIdBadFormatting, PlateBarcodeBadFormat, \
    SampleNotFound, WellPositionOccupied, OccupiedDestinationTube, TubeNotFound
from init_db import EngineCreator, Base
from dotenv import load_dotenv

from reports import print_report, WellPositionBadFormatting


def read_database_credentials_from_env(type: str) -> tp.Dict[str, tp.Any]:
    """
    Read database credentials from environment variables
    :param type: PROD or TEST
    :return: credentials in format for passing into create_engine function
    """
    credentials = {
        "user": force_get_env_var(f"{type}_DATABASE_USER"),
        "password": force_get_env_var(f"{type}_DATABASE_PASSWORD"),
        "host": force_get_env_var(f"{type}_DATABASE_HOST"),
        "port": force_get_env_var(f"{type}_DATABASE_PORT"),
        "database_name": force_get_env_var(f"{type}_DATABASE_NAME")
    }

    PROD_DATABASE_TYPE = force_get_env_var(f"{type}_DATABASE_TYPE")

    if PROD_DATABASE_TYPE.lower() == "postgresql":
        credentials["database"] = "postgresql+psycopg2"

    return credentials


class DatabaseInitializer:

    def initalize(self, recreate: bool = False) -> Engine:
        load_dotenv()
        database_arguments = read_database_credentials_from_env("PROD")

        engine = EngineCreator.create_engine(**database_arguments)

        if not database_exists(engine.url):
            create_database(engine.url)
        if recreate:
            Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

        return engine


class MyCLIApp(cmd2.Cmd):
    """CLI tool for tracking samples."""

    # Setting the prompt
    prompt = "sanger-sample-tool> "

    def __init__(self, database_layer: DatabaseLayer):
        super().__init__()

        self.database_layer = database_layer

    record_receipt_parser = cmd2.Cmd2ArgumentParser()
    record_receipt_parser.add_argument('customer_sample_name', help='Customer sample name')
    record_receipt_parser.add_argument('tube_barcode', help='Tube barcode, format: NT<Number>')
    # Command to simulate record_receipt

    @cmd2.with_argparser(record_receipt_parser)
    def do_record_receipt(self, args):
        """Record a receipt: record_receipt [customer_sample_name] [tube_barcode]"""
        try:
            self.database_layer.record_receipt(args.customer_sample_name, args.tube_barcode)
        except TubeBarcodeBadFormat:
            self.poutput(f"Bad barcode: {args.tube_barcode}. Expected NT<Number>")
            return
        except SampleAlreadyReceived:
            self.poutput(f"Sample in tube [{args.tube_barcode}] was already received.")
            return

        self.poutput(f"Successfully recorded receipt: {args.customer_sample_name} [{args.tube_barcode}]")

    add_to_plate_parser = cmd2.Cmd2ArgumentParser()
    add_to_plate_parser.add_argument('sample_id', help='Sample name', type=int)
    add_to_plate_parser.add_argument('plate_barcode', help='Plate barcode, format: DN<Number>')
    add_to_plate_parser.add_argument('well_position', help='Well position, format: <Row><Col>: A1, B8')

    @cmd2.with_argparser(add_to_plate_parser)
    def do_add_to_plate(self, args):
        """Add sample to plate: add_to_plate [sample_id] [plate_barcode] [well_position]"""
        try:
            self.database_layer.add_to_plate(args.sample_id, args.plate_barcode, args.well_position)
        except SampleIdBadFormatting:
            self.poutput(f"Bad sample id: {args.sample_id}. Expected NT<PositiveNumber>")
            return
        except PlateBarcodeBadFormat:
            print(f'Plate barcode wrong format. Expected: "DN<Number>". Got: {args.plate_barcode}')
            return
        except WellPositionBadFormatting:
            print(f'Well position wrong format. Expected: "<Letter [A-H]><Number [1-12]>". Got: {args.well_position}')
            return
        except SampleNotFound:
            print(f"Sample (id: {args.sample_id}) not found in table.")
            return
        except WellPositionOccupied:
            print(f"Well at position {args.well_position} already occupied.")
            return

        self.poutput(f"Successfully added sample (id: {args.sample_id}) to plate {args.plate_barcode} at {args.well_position}")

    tube_transfer_parser = cmd2.Cmd2ArgumentParser()
    tube_transfer_parser.add_argument('source_tube_barcode', help='Source tube barcode. Format: NT<Number>')
    tube_transfer_parser.add_argument('destination_tube_barcode', help='Destination tube barcode. Format: NT<Number>')

    @cmd2.with_argparser(tube_transfer_parser)
    def do_tube_transfer(self, args):
        """Transfer sample from one tube to another: tube_transfer [source_tube_barcode] [destination_tube_barcode]"""
        try:
            self.database_layer.tube_transfer(args.source_tube_barcode, args.destination_tube_barcode)
        except TubeBarcodeBadFormat:
            self.poutput(f"Bad tube barcode format: {args.source_tube_barcode} / {args.destination_tube_barcode}. "
                         f"Should be: NT<Number>")
            return
        except OccupiedDestinationTube:
            self.poutput(f"Destination tube ({args.destination_tube_barcode}) is already occupied.")
            return
        except TubeNotFound:
            print(f'Source tube ({args.source_tube_barcode}) is empty.')
            return

        self.poutput(f"Successfully transfer sample from tube ({args.source_tube_barcode}) "
                     f"to tube ({args.destination_tube_barcode})")


if __name__ == '__main__':
    engine = DatabaseInitializer().initalize()

    connection = engine.connect()

    Session = sessionmaker(bind=connection)
    session = Session()

    app = MyCLIApp(database_layer=DatabaseLayer(session))
    app.cmdloop()
