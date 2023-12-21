class BadFunctionSignature(Exception):
    pass

class BadBarcodeFormat(Exception):
    pass

class SampleAlreadyReceived(Exception):
    # Duplicate barcodes
    pass

def record_receipt(customer_sample_name: str, tube_barcode: str) -> int:
    """
    :param customer_sample_name: str, any format
    :param tube_barcode: str, format: NT<number>
    :return: Sample ID
    """
    pass
