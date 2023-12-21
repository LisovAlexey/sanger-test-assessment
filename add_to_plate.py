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


def add_to_plate(sample_id: int, plate_barcode: str, well_position: str) -> None:
    """
    Adds sample to well in specified plate
    :param sample_id: int, positive
    :param plate_barcode: str, format: "DN<number>"
    :param well_position: str, format: "<Row><Column>" where <Row> is Char from A to H and <Column> is int from 1 to 12
    :return:
    """
    pass