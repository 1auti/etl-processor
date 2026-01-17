from core.exceptions.etl_exception import EtlException


class ParsingError(EtlException):
    """Error durante el parseo de logs"""
    pass
