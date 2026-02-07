from src.core.exceptions.parsing.parsing_exception import ParsingError


class UnsupportedLogFormatError(ParsingError):
    """El formato del log no esta soportada"""
