from init_db import Well, Sample


class DatabaseLayer:
    # Store db connection and give users point to connect

    def __init__(self, connection):
        self.connection = connection

    def add_to_plate(self, sample_id: int, plate_barcode: str, well_position: str) -> Well:
        """
        Adds sample to well in specified plate
        :param sample_id: int, positive
        :param plate_barcode: str, format: "DN<number>"
        :param well_position: str, format: "<Row><Column>" where <Row> is Char from A to H and <Column> is int from 1 to 12
        :return:
        """
        pass

    def record_receipt(self, customer_sample_name: str, tube_barcode: str) -> Sample:
        """
        :param customer_sample_name: str, any format
        :param tube_barcode: str, format: NT<number>
        :return: Sample ID
        """
        pass


class SampleIdBadFormatting(Exception):
    pass


class SampleNotFound(Exception):
    pass


class PlateBarcodeBadFormatting(Exception):
    pass


class WellPositionBadFormatting(Exception):
    pass


class WellPositionOutOfBounds(Exception):
    pass


class WellPositionOccupied(Exception):
    pass


class BadFunctionSignature(Exception):
    pass


class BadBarcodeFormat(Exception):
    pass


class SampleAlreadyReceived(Exception):
    # Duplicate barcodes
    pass

