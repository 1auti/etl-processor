from src.core.exceptions.etl_exception import EtlException


class EnrichmentError(EtlException):
    """Error durante el enriquecimiento de datos"""
