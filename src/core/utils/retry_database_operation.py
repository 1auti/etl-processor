import functools
import time
from typing import Callable

from core import logger


def retry_database_operation(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0
):
    """
    Decorador especializado para operaciones de base de datos.
    Captura excepciones comunes de bases de datos.
    """
    import psycopg2
    import mysql.connector

    database_exceptions = (
        psycopg2.OperationalError,
        psycopg2.InterfaceError,
        mysql.connector.Error,
        ConnectionError,
        TimeoutError
    )

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 1
            current_delay = delay

            while attempt <= max_attempts:
                try:
                    return func(*args, **kwargs)

                except database_exceptions as e:
                    if attempt == max_attempts:
                        logger.error(
                            f" Operación de base de datos {func.__name__} falló después de {max_attempts} intentos: {e}"
                        )
                        raise

                    logger.warning(
                        f" {func.__name__} falló (intento {attempt}/{max_attempts}). "
                        f"Posible problema de conexión. Reintentando en {current_delay}s..."
                    )

                    # Intentar resetear la conexión si es posible
                    if hasattr(args[0], 'reset_connection'):
                        try:
                            args[0].reset_connection()
                        except Exception:
                            pass

                    time.sleep(current_delay)
                    attempt += 1
                    current_delay *= backoff

        return wrapper
    return decorator
