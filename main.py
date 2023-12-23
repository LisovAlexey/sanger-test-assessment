# This is a sample Python script.
import typing as tp

from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database

from database import DatabaseLayer
from env import force_get_env_var
from init_db import EngineCreator, Base
from dotenv import load_dotenv

from reports import print_report


def parse_args(args: tp.List[tp.Tuple[str, tp.Type]]) -> tp.Dict[str, tp.Any]:
    result = {}
    for (arg, _type) in args:
        validated = False
        while not validated:
            user_input = input("Please provide " + arg + ": ")
            try:
                result[arg] = _type(user_input)
                validated = True
            except Exception as e:
                print(str(e))
    return result


def read_commands(database_layer: DatabaseLayer) -> None:
    user_input = input("Enter your command (type 'exit' to quit): ")

    # Check if the user wants to exit
    if user_input.lower() == 'exit':
        print("Exiting the program.")
        exit()
    elif user_input.lower() == 'record_receipt':
        kwargs = parse_args([("customer_sample_name", str), ("tube_barcode", str)])
        sample = database_layer.record_receipt(**kwargs)
        print("New sample id: " + str(sample.id))
    elif user_input.lower() == 'add_to_plate':
        kwargs = parse_args([("sample_id", int), ("plate_barcode", str), ("well_position", str)])
        database_layer.add_to_plate(**kwargs)
        print("Successful addition")
    elif user_input.lower() == 'tube_transfer':
        kwargs = parse_args([("source_tube_barcode", str), ("destination_tube_barcode", str)])
        database_layer.tube_transfer(**kwargs)
        print("Successful tube transfer")
    elif user_input.lower() == 'list_samples_in':
        kwargs = parse_args([("container_barcode", str)])
        report = database_layer.list_samples_in(**kwargs)
        print(print_report(report))
    else:
        print(f"Command {user_input} not found")


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


if __name__ == "__main__":
    load_dotenv()

    # init_db
    engine = EngineCreator.create_engine(**read_database_credentials_from_env("PROD"))

    if not database_exists(engine.url):
        create_database(engine.url)
    Base.metadata.create_all(engine)

    connection = engine.connect()

    Session = sessionmaker(bind=connection)
    session = Session()
    database_layer = DatabaseLayer(session)

    while True:
        try:
            read_commands(database_layer)
        except Exception as e:
            print(repr(e), str(e))
