from core.exceptions.etl_exception import EtlException


class StorageError(EtlException):
    """Error relacionado con la capa de persistencia"""
    pass
