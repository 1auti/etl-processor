from core.exceptions.etl_exception import EtlException
from core.exceptions.parsing.parsing_exception import ParsingError


class UnsupportedLogFormatError(ParsingError()):
    """El formato del log no esta soportada"""
    pass



