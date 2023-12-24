class BaseApplicationException(Exception):
    """Base class for exceptions in this module."""


class FormattingException(BaseApplicationException):
    """Base exception for formatting errors."""


class BarcodeBadFormat(FormattingException):
    def __init__(self, barcode: str, *args, **kwargs):
        default_message = f'Bad barcode format. Expected: "DN<Number>" for plate or "NT<Number>" for tube. Got: f{barcode}'
        super().__init__(default_message, *args, **kwargs)


class TubeBarcodeBadFormat(BarcodeBadFormat):
    def __init__(self, barcode: str, *args, **kwargs):
        default_message = f'Tube barcode wrong format. Expected: "NT<Number>". Got: f{barcode}'
        super().__init__(default_message, *args, **kwargs)


class PlateBarcodeBadFormat(BarcodeBadFormat):
    def __init__(self, barcode: str, *args, **kwargs):
        default_message = f'Plate barcode wrong format. Expected: "DN<Number>". Got: f{barcode}'
        super().__init__(default_message, *args, **kwargs)


class OccupiedDestinationTube(BaseApplicationException):
    def __init__(self, tube_barcode: str, *args, **kwargs):
        default_message = f'Tube with barcode {tube_barcode} already occupied.'
        super().__init__(default_message, *args, **kwargs)


class SampleNotFound(BaseApplicationException):
    def __init__(self, sample_id: int, *args, **kwargs):
        default_message = f'sample_id {sample_id} not found in table.'
        super().__init__(default_message, *args, **kwargs)


class SampleIdBadFormatting(FormattingException):
    def __init__(self, sample_id: int, *args, **kwargs):
        default_message = f'sample_id {sample_id} bad format. Expected positive number.'
        super().__init__(default_message, *args, **kwargs)


class TubeNotFound(BaseApplicationException):
    def __init__(self, tube_barcode: str, *args, **kwargs):
        default_message = f'Tube with {tube_barcode} not found.'
        super().__init__(default_message, *args, **kwargs)


class OccupiedWellsNotFound(BaseApplicationException):
    def __init__(self, plate_barcode: str, *args, **kwargs):
        default_message = f'Occupied wells not found for {plate_barcode}.'
        super().__init__(default_message, *args, **kwargs)


class SampleAlreadyReceived(BaseApplicationException):
    # Duplicate barcodes
    def __init__(self, tube_barcode: str, *args, **kwargs):
        default_message = f'Sample already received for {tube_barcode}.'
        super().__init__(default_message, *args, **kwargs)


class WellPositionOccupied(BaseApplicationException):
    def __init__(self, well_position: str, plate_barcode: str, *args, **kwargs):
        default_message = f'Position {well_position} already occupied in plate {plate_barcode}.'
        super().__init__(default_message, *args, **kwargs)
