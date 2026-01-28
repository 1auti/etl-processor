from src.core.exceptions.parsing.parsing_exception import ParsingError


class InvalidLogFormatError(ParsingError):
    """El formato del log no es reconocido"""
