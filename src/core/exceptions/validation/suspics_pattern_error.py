from src.core.exceptions.validation.validation_error import ValidationError


class SuspiciousPatternError(ValidationError):
    """Patron sospechoso detectado (SQL Inyection, XSS, etc)"""
    pass
