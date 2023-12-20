class BadBarcodeFormat(Exception):
    pass

class SampleAlreadyReceived(Exception):
    # Duplicate barcodes
    pass

def record_receipt(customer_sample_name: str, tube_barcode: str) -> str:
    pass


record_receipt(1, 1)