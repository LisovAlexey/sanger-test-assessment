import typing as tp

from exceptions import WellPositionBadFormatting, UnknownReportType
from format_validator import well_position_validator
from database.scheme import Sample, Well


class WellPositionFormatAdapter:
    @staticmethod
    def get_row_col_position(well_position: str) -> tp.Tuple[int, int]:
        letter_row, letter_col = well_position_validator.extract(well_position)[0]
        row = ord(letter_row) + 1 - ord('A')
        col = int(letter_col)

        if row <= 0 or row > 8 or col <= 0 or col > 12:
            raise WellPositionBadFormatting(well_position=well_position)
        return row, col

    @staticmethod
    def get_string_position(row: int, col: int) -> str:
        return f"{chr(row - 1 + ord('A'))}{col}"


class TubeReport:
    def __init__(self, tube_barcode: str, sample_id: int, customer_sample_name: str):
        self.barcode = tube_barcode
        self.sample_id = sample_id
        self.customer_sample_name = customer_sample_name


class PlateReport:
    def __init__(self, plate_barcode: str, wells_and_samples: tp.List[tp.Tuple[Well, Sample]]):
        self.barcode = plate_barcode
        self.wells_and_samples = wells_and_samples


class PlateReportFormatter:
    @staticmethod
    def format(plate_report: PlateReport) -> str:
        result = f"""
        ======== Plate: {plate_report.barcode} ========
        """

        for (well, sample) in plate_report.wells_and_samples:
            result += f"""
            Well position: {WellPositionFormatAdapter.get_string_position(row=well.row, col=well.col)}
            Sample ID: {well.sample_id}
            Customer Sample Name: {sample.customer_sample_name}
            """

        return result


class TubeReportFormatter:
    @staticmethod
    def format(tube_report: TubeReport) -> str:
        return f"""
        ======== Tube: {tube_report.barcode} ========
        Sample ID: {tube_report.sample_id}
        Customer Sample Name: {tube_report.customer_sample_name}
        """


def print_report(report: tp.Union[PlateReport, TubeReport]) -> str:
    if isinstance(report, PlateReport):
        return PlateReportFormatter.format(plate_report=report)
    elif isinstance(report, TubeReport):
        return TubeReportFormatter.format(tube_report=report)
    else:
        raise UnknownReportType
