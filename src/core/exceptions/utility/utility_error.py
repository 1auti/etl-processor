from src.core.exceptions.etl_exception import EtlException


def format_exception(exc: Exception) -> dict:
    """Formatea una excepcion para logging estructurado

    Args:
         exc: Exception a formatear
    Return:
         dict:Diccionario con informacion de la exception
    """

    result = {
        "exception_type":type(exc).__name__,
        "message":str(exc),
    }

    #Si es una exception custom agregar detalles
    if isinstance(exc, EtlException):
        result["details"] = exc.details

    return result
