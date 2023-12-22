import typing as tp

from init_db import Well


class TubeReport:
    def __init__(self, tube_barcode: str, sample_id: int, customer_sample_name: str):
        self.barcode = tube_barcode
        self.sample_id = sample_id
        self.customer_sample_name = customer_sample_name


class PlateReport:
    def __init__(self, plate_barcode: str, wells: tp.List[Well]):
        self.barcode = plate_barcode
        self.wells = wells
