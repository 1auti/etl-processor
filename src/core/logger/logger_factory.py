import structlog


def get_logger(name: str = None) -> structlog.BoundLogger:
    """
    Obtiene un logger estructurado.

    Args:
        name: Nombre del logger (generalmente __name__ del módulo)

    Returns:
        BoundLogger configurado

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Processing file", filename="logs.txt", lines=1000)
    """
    return structlog.get_logger(name or __name__)
