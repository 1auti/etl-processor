from core.exceptions.etl_exception import EtlException
from core.exceptions.parsing.parsing_exception import ParsingError


class InvalidLogFormatError(ParsingError):
    """El formato del log no es reconocido"""
    pass


