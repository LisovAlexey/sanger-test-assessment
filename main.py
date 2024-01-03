# This is a sample Python script.
import cmd2

from sqlalchemy.orm import sessionmaker

from database.database import DatabaseLayer
from database.management import DatabaseInitializer, DatabaseArgumentsLoader
from exceptions import TubeBarcodeBadFormat, SampleAlreadyReceived, SampleIdBadFormatting, PlateBarcodeBadFormat, \
    SampleNotFound, WellPositionOccupied, OccupiedDestinationTube, TubeNotFound, BarcodeBadFormat, OccupiedWellsNotFound

from reports import WellPositionBadFormatting, print_report
from database.scheme import Base


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
            self.perror(f"Bad barcode: {args.tube_barcode}. Expected NT<Number>")
            return
        except SampleAlreadyReceived:
            self.perror(f"Sample in tube [{args.tube_barcode}] was already received.")
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
            self.perror(f"Bad sample id: {args.sample_id}. Expected NT<PositiveNumber>")
            return
        except PlateBarcodeBadFormat:
            self.perror(f'Plate barcode wrong format. Expected: "DN<Number>". Got: {args.plate_barcode}')
            return
        except WellPositionBadFormatting:
            self.perror(
                f'Well position wrong format. Expected: "<Letter [A-H]><Number [1-12]>". Got: {args.well_position}')
            return
        except SampleNotFound:
            self.perror(f"Sample (id: {args.sample_id}) not found in table.")
            return
        except WellPositionOccupied:
            self.perror(f"Well at position {args.well_position} already occupied.")
            return

        self.poutput(
            f"Successfully added sample (id: {args.sample_id}) to plate {args.plate_barcode} at {args.well_position}")

    tube_transfer_parser = cmd2.Cmd2ArgumentParser()
    tube_transfer_parser.add_argument('source_tube_barcode', help='Source tube barcode. Format: NT<Number>')
    tube_transfer_parser.add_argument('destination_tube_barcode', help='Destination tube barcode. Format: NT<Number>')

    @cmd2.with_argparser(tube_transfer_parser)
    def do_tube_transfer(self, args):
        """Transfer sample from one tube to another: tube_transfer [source_tube_barcode] [destination_tube_barcode]"""
        try:
            self.database_layer.tube_transfer(args.source_tube_barcode, args.destination_tube_barcode)
        except TubeBarcodeBadFormat:
            self.perror(f"Bad tube barcode format: {args.source_tube_barcode} / {args.destination_tube_barcode}. "
                        f"Should be: NT<Number>")
            return
        except OccupiedDestinationTube:
            self.perror(f"Destination tube ({args.destination_tube_barcode}) is already occupied.")
            return
        except TubeNotFound:
            self.perror(f'Source tube ({args.source_tube_barcode}) is empty.')
            return

        self.poutput(f"Successfully transfer sample from tube ({args.source_tube_barcode}) "
                     f"to tube ({args.destination_tube_barcode})")

    list_samples_in_parser = cmd2.Cmd2ArgumentParser()
    list_samples_in_parser.add_argument('container_barcode', help='Tube or plate barcode. Format: '
                                                                  'NT<Number> / DN<Number>')

    @cmd2.with_argparser(list_samples_in_parser)
    def do_list_samples_in(self, args):
        """Print report for tube or plate: list_samples_in [container_barcode]"""
        try:
            report = self.database_layer.list_samples_in(args.container_barcode)
        except TubeNotFound:
            self.perror(f"Tube with barcode {args.container_barcode} not found.")
            return
        except OccupiedWellsNotFound:
            self.perror(f"No occupied wells found for barcode {args.container_barcode}")
            return
        except BarcodeBadFormat:
            self.perror(f'Barcode ({args.container_barcode}) has invalid format. Expected NT<Number> / DN<Number>')
            return

        self.poutput(print_report(report))


if __name__ == '__main__':
    database_arguments = DatabaseArgumentsLoader.load_database_arguments("PROD")
    engine = DatabaseInitializer(Base=Base).initialize(database_arguments, recreate=False)

    connection = engine.connect()

    Session = sessionmaker(bind=connection)
    session = Session()

    app = MyCLIApp(database_layer=DatabaseLayer(session))
    app.cmdloop()
