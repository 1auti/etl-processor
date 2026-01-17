from xml.dom import ValidationErr


class InvalidTimestampError(ValidationErr()):
    """Timesstamp invalido o fuera de rango"""
pass
