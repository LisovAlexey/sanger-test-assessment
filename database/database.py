import typing as tp

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from exceptions import BarcodeBadFormat, TubeBarcodeBadFormat, PlateBarcodeBadFormat, OccupiedDestinationTube, \
    SampleNotFound, SampleIdBadFormatting, TubeNotFound, OccupiedWellsNotFound, SampleAlreadyReceived, \
    WellPositionOccupied, WellPositionBadFormatting
from database.scheme import Sample, Well
from reports import TubeReport, PlateReport, WellPositionFormatAdapter

from format_validator import tube_barcode_validator, plate_barcode_validator, well_position_validator


class DatabaseLayer:
    # Store db connection and give users point to connect

    def __init__(self, session: Session):
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
            raise SampleAlreadyReceived(tube_barcode=tube_barcode) from exc

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

        row, col = WellPositionFormatAdapter.get_row_col_position(well_position=well_position)

        query = self.session.query(Sample.id).filter(Sample.id == sample_id)
        if not self.session.query(query.exists()).scalar():
            raise SampleNotFound(sample_id=sample_id)

        well = Well(sample_id=sample_id, plate_barcode=plate_barcode, col=col, row=row)
        self.session.add(well)
        try:
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()
            raise WellPositionOccupied(well_position=well_position, plate_barcode=plate_barcode) from exc

        return well

    def list_samples_in(self, container_barcode: str) -> tp.Union[TubeReport, PlateReport]:
        """
        :param container_barcode: str Tube: [NT<number>] or Plate: [DN<number>]
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
            assert fetched_sample.customer_sample_name is not None
            return TubeReport(
                tube_barcode=tube_barcode,
                sample_id=fetched_sample.id,
                customer_sample_name=fetched_sample.customer_sample_name
            )

    def _get_plate_report(self, plate_barcode: str) -> PlateReport:
        fetched_wells_and_samples = (
            self.session.query(Well, Sample)
                .join(Well, Sample.id == Well.sample_id)
                .filter(Well.plate_barcode == plate_barcode)
                .all()
        )

        # Convert to list[tuple(Well, Sample)]
        fetched_wells_and_samples_converted = [(well, sample) for (well, sample) in fetched_wells_and_samples]

        if not fetched_wells_and_samples:
            raise OccupiedWellsNotFound(plate_barcode=plate_barcode)
        else:
            return PlateReport(
                plate_barcode=plate_barcode,
                wells_and_samples=fetched_wells_and_samples_converted
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


