from src.core.exceptions.etl_exception import EtlException


class RetryExhaustedError(EtlException):
    """Se agotaron todos los reintentos"""

    def __init__(self, message: str, attemps: int, last_error: Exception):
        super().__init__(message, {"attempts": attemps})
        self.attemps = attemps
        self.last_error = last_error
