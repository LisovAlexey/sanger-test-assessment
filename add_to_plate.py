class SampleIdBadFormatting(Exception):
    pass

class SampleNotFound(Exception):
    pass

class PlateBarcodeBadFormatting(Exception):
    pass

class WellPositionBadFormatting(Exception):
    pass

class WellPositionOccupied(Exception):
    pass


def add_to_plate(sample_id: int, plate_barcode: str, well_position: str):
    pass

"""
Qustions:
1. Should the plate be created or it will be created when adding to the plate?
2. What the 'An individual sample can be added to one or many wells.' exactly means? 
So, does one sample has only one tube? If so, then how sample can be added to several wells?
If no, then how we put sample in several tubes? We always receive sample(and generate new sample id) to new tube. 
And when sample transferred from one tube to another the source tube is empty. 
So we can't have two tubes with the same sample.
"""