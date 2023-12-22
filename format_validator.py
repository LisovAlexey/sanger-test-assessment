import re
class RegexFormatValidator:
    def __init__(self, regex_format: str):
        self.regex_format = regex_format

    def validate(self, string: str) -> bool:
        return re.match(self.regex_format, string)

tube_barcode_validator = RegexFormatValidator(regex_format="^NT\d+$")
plate_barcode_validator = RegexFormatValidator(regex_format="^DN\d+$")