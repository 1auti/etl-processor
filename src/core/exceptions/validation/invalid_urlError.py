from core.exceptions.validation.validation_error import ValidationError


class invalidUrlError(ValidationError()):
    """URL mal formada o sospechosa"""
    pass


