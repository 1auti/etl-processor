from xml.dom import ValidationErr


class InvalidStatusCodeError(ValidationErr()):
    """Metodo de status no valido"""
    pass

