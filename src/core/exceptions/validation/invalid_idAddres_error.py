from core.exceptions.etl_exception import EtlException
from core.exceptions.validation.validation_error import ValidationError


class InvalidIpAddresError(ValidationError()):
    """Direccion IP invalida"""
    pass



