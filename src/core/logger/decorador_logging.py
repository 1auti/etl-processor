"""
Decoradores para logging de funciones.

Proporciona decoradores para registrar automáticamente entrada, salida
y errores en funciones.
"""

import functools
import time

import structlog

from .logger_factory import get_logger


def log_function_call(logger: structlog.BoundLogger = None):
    """
    Decorador que loguea entrada y salida de funciones.

    Args:
        logger: Logger opcional. Si no se proporciona, se crea uno automáticamente.

    Example:
        >>> logger = get_logger(__name__)
        >>> @log_function_call(logger)
        ... def process_data(data):
        ...     return len(data)
    """

    def decorator(func):
        nonlocal logger
        if logger is None:
            logger = get_logger(func.__module__)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Log entrada
            logger.debug(
                "Function called",
                function=func.__name__,
                args_count=len(args),
                kwargs_keys=list(kwargs.keys()),
            )

            start_time = time.time()

            try:
                result = func(*args, **kwargs)

                # Log salida exitosa
                duration = time.time() - start_time
                logger.debug(
                    "Function completed",
                    function=func.__name__,
                    duration_seconds=round(duration, 3),
                )

                return result

            except Exception as e:
                # Log error
                duration = time.time() - start_time
                logger.error(
                    "Function failed",
                    function=func.__name__,
                    duration_seconds=round(duration, 3),
                    error=str(e),
                    error_type=type(e).__name__,
                )
                raise

        return wrapper

    return decorator
