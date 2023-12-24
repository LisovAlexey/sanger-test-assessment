# This is a sample Python script.
import typing as tp
import argparse
import cmd2
from sqlalchemy import Engine

from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database

from database.database import DatabaseLayer
from env import force_get_env_var
from exceptions import TubeBarcodeBadFormat, SampleAlreadyReceived
from init_db import EngineCreator, Base
from dotenv import load_dotenv

from reports import print_report



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

    name_parser = cmd2.Cmd2ArgumentParser()
    name_parser.add_argument('customer_sample_name', help='Customer sample name')
    name_parser.add_argument('tube_barcode', help='Tube barcode, format: NT<Number>')
    # Command to simulate record_receipt

    @cmd2.with_argparser(name_parser)
    def do_record_receipt(self, args):
        """Record a receipt: record_receipt [customer_sample_name] [tube_barcode]"""
        try:
            self.database_layer.record_receipt(args.customer_sample_name, args.tube_barcode)
        except TubeBarcodeBadFormat:
            print(f"Bad barcode: {args.tube_barcode}. Expected NT<Number>")
            return
        except SampleAlreadyReceived:
            print(f"Sample in tube [{args.tube_barcode}] was already received.")
            return

        self.poutput(f"Successfully recorded receipt: {args.customer_sample_name} [{args.tube_barcode}]")


if __name__ == '__main__':
    engine = DatabaseInitializer().initalize()

    connection = engine.connect()

    Session = sessionmaker(bind=connection)
    session = Session()

    app = MyCLIApp(database_layer=DatabaseLayer(session))
    app.cmdloop()
