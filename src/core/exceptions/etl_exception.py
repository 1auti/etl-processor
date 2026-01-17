class EtlException(Exception):
    """Excepcion base para todos los errores del ETL
    TOdas las exceptions custom heredan de esta
    """

def __init__(self,message:str, details: dict = None):
    """
    Args:
    message: Mensaje descriptivo del error
    details: Diccionnario con infomracion adicional del contexto
    """

    super().__init__(message)
    self.message = message
    self.details = details or {}

def __str__(self):
    if self.details:
        details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
        return f"{self.message} [{details_str}]"

    return self.message





