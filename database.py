import typing as tp

from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from init_db import Well, Sample
from reports import TubeReport, PlateReport

from format_validator import tube_barcode_validator, plate_barcode_validator, well_position_validator


class TubeBarcodeBadFormat(Exception):
    def __init__(self, barcode: str, *args, **kwargs):
        default_message = f'Tube barcode wrong format. Expected: "NT<Number>". Got: f{barcode}'
        super().__init__(default_message, *args, **kwargs)

class PlateBarcodeBadFormat(Exception):
    def __init__(self, barcode: str, *args, **kwargs):
        default_message = f'Plate barcode wrong format. Expected: "DN<Number>". Got: f{barcode}'
        super().__init__(default_message, *args, **kwargs)

class BarcodeBadFormat(Exception):
    def __init__(self, barcode: str, *args, **kwargs):
        default_message = f'Bad barcode format. Expected: "DN<Number>" for plate or "NT<Number>" for tube. Got: f{barcode}'
        super().__init__(default_message, *args, **kwargs)

class WellPositionBadFormatting(Exception):
    def __init__(self, well_position: str, *args, **kwargs):
        default_message = f'Well position wrong format. Expected: "<Letter [A-H]><Number [1-12]>". Got: f{well_position}'
        super().__init__(default_message, *args, **kwargs)

class OccupiedDestinationTube(Exception):
    def __init__(self, tube_barcode: str, *args, **kwargs):
        default_message = f'Tube with barcode {tube_barcode} already occupied.'
        super().__init__(default_message, *args, **kwargs)

class SampleNotFound(Exception):
    def __init__(self, sample_id: int, *args, **kwargs):
        default_message = f'sample_id {sample_id} not found in table.'
        super().__init__(default_message, *args, **kwargs)


class SampleIdBadFormatting(Exception):
    def __init__(self, sample_id: int, *args, **kwargs):
        default_message = f'sample_id {sample_id} bad format. Expected positive number.'
        super().__init__(default_message, *args, **kwargs)


class TubeNotFound(Exception):
    def __init__(self, tube_barcode: str, *args, **kwargs):
        default_message = f'Tube with {tube_barcode} not found.'
        super().__init__(default_message, *args, **kwargs)

class OccupiedWellsNotFound(Exception):
    def __init__(self, plate_barcode: str, *args, **kwargs):
        default_message = f'Occupied wells not found for {plate_barcode}.'
        super().__init__(default_message, *args, **kwargs)



class DatabaseLayer:
    # Store db connection and give users point to connect

    def __init__(self, session):
        self.session = session

    def record_receipt(self, customer_sample_name: str, tube_barcode: str) -> Sample:
        """
        :param customer_sample_name: str, any format
        :param tube_barcode: str, format: NT<number>
        :return: Sample ID
        """

        if not tube_barcode_validator.validate(tube_barcode):
            raise TubeBarcodeBadFormat(tube_barcode)

        sample = Sample(customer_sample_name=customer_sample_name, tube_barcode=tube_barcode)
        self.session.add(sample)
        try:
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()
            raise SampleAlreadyReceived from exc

        return sample

    def add_to_plate(self, sample_id: int, plate_barcode: str, well_position: str) -> Well:
        """
        Adds sample to well in specified plate
        :param sample_id: int, positive
        :param plate_barcode: str, format: "DN<number>"
        :param well_position: str, format: "<Row><Column>" where <Row> is Char from A to H and <Column> is int from 1 to 12
        :return:
        """

        if sample_id <= 0:
            raise SampleIdBadFormatting(sample_id=sample_id)

        if not plate_barcode_validator.validate(plate_barcode):
            raise PlateBarcodeBadFormat(barcode=plate_barcode)

        well_position = well_position.upper()

        if not well_position_validator.validate(well_position):
            raise WellPositionBadFormatting(well_position=well_position)

        letter_row, letter_col = well_position_validator.extract(well_position)[0]
        row = ord(letter_row) - ord('A') + 1
        col = int(letter_col)

        if row <= 0 or row > 8 or col <= 0 or col > 12:
            raise WellPositionBadFormatting(well_position=well_position)

        query = self.session.query(Sample.id).filter(Sample.id == sample_id)
        if not self.session.query(query.exists()).scalar():
            raise SampleNotFound(sample_id=sample_id)

        well = Well(sample_id=sample_id, plate_barcode=plate_barcode, col=col, row=row)
        self.session.add(well)
        try:
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()
            raise WellPositionOccupied from exc

        return well


    def list_samples_in(self, container_barcode: str) -> tp.Union[TubeReport, PlateReport]:
        """
        :param container_barcode: str Tube: [NT<number>]  or Plate: [DN<number>]
        :return: report for specified container
        """

        if tube_barcode_validator.validate(container_barcode):
            return self._get_tube_report(tube_barcode=container_barcode)
        elif plate_barcode_validator.validate(container_barcode):
            return self._get_plate_report(plate_barcode=container_barcode)
        else:
            raise BarcodeBadFormat(barcode=container_barcode)

    def _get_tube_report(self, tube_barcode: str) -> TubeReport:

        fetched_sample = self.session.query(Sample).filter(Sample.tube_barcode == tube_barcode).first()
        if fetched_sample is None:
            raise TubeNotFound(tube_barcode=tube_barcode)
        else:
            return TubeReport(
                tube_barcode=tube_barcode,
                sample_id=fetched_sample.id,
                customer_sample_name=fetched_sample.customer_sample_name
            )


    def _get_plate_report(self, plate_barcode: str) -> PlateReport:
        fetched_wells = self.session.query(Well).filter(Well.plate_barcode == plate_barcode).all()
        if not fetched_wells:
            raise OccupiedWellsNotFound(plate_barcode=plate_barcode)
        else:
            return PlateReport(
                plate_barcode=plate_barcode,
                wells=fetched_wells
            )

    def tube_transfer(self, source_tube_barcode: str, destination_tube_barcode: str) -> None:
        """
        :param source_tube_barcode: str, format: NT<number>
        :param destination_tube_barcode: str, format: NT<number>
        :return: None
        """

        if not tube_barcode_validator.validate(source_tube_barcode):
            raise TubeBarcodeBadFormat(barcode=source_tube_barcode)

        if not tube_barcode_validator.validate(destination_tube_barcode):
            raise TubeBarcodeBadFormat(barcode=destination_tube_barcode)

        fetched_dest_sample = self.session.query(Sample).filter(Sample.tube_barcode == destination_tube_barcode).first()

        if fetched_dest_sample:
            raise OccupiedDestinationTube(tube_barcode=destination_tube_barcode)

        fetched_source_sample = self.session.query(Sample).filter(Sample.tube_barcode == source_tube_barcode).first()

        if not fetched_source_sample:
            raise TubeNotFound(tube_barcode=source_tube_barcode)

        fetched_source_sample.tube_barcode = destination_tube_barcode

        try:
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()


class WellPositionOccupied(Exception):
    pass


class BadFunctionSignature(Exception):
    pass


class SampleAlreadyReceived(Exception):
    # Duplicate barcodes
    pass


class ContainerBarcodeBadFormatting(Exception):
    pass




