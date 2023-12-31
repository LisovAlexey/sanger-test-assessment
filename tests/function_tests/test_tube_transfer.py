import pytest
from exceptions import TubeBarcodeBadFormat, OccupiedDestinationTube, TubeNotFound


class TestTubeTransfer:

    def test_tube_transfer(self, database_layer, sample_one):
        database_layer.tube_transfer(sample_one.tube_barcode, "NT999")
        assert sample_one.tube_barcode == "NT999"

    def test_tube_transfer_bad_format(self, database_layer, sample_one):
        with pytest.raises(TubeBarcodeBadFormat):
            database_layer.tube_transfer(sample_one.tube_barcode, "999")

    def test_tube_transfer_not_existing_source_tube(self, database_layer):
        with pytest.raises(TubeNotFound):
            database_layer.tube_transfer("NT100000", "NT999")

    def test_tube_transfer_occupied_destination_tube(self, sample_one, sample_two, database_layer):
        with pytest.raises(OccupiedDestinationTube):
            database_layer.tube_transfer(sample_one.tube_barcode, sample_two.tube_barcode)
