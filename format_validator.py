import re
import typing as tp


class RegexFormatExtractor:
    def __init__(self, regex_format: str):
        self.regex_format = regex_format

    def validate(self, string: str) -> bool:
        return bool(re.findall(self.regex_format, string))

    def extract(self, string: str) -> tp.List[tp.Tuple[str, ...]]:
        return re.findall(self.regex_format, string)


tube_barcode_validator = RegexFormatExtractor(regex_format=r"^NT\d+$")
plate_barcode_validator = RegexFormatExtractor(regex_format=r"^DN\d+$")

well_position_validator = RegexFormatExtractor(regex_format=r"^([A-H])([1-9]\d*)$")
