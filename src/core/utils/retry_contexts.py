from contextlib import contextmanager
import time
from typing import Tuple, Type

from core import logger


@contextmanager
def retry_context(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    operation_name: str = "operation"
):
    """
    Context manager para reintentos de bloques de código.

    Example:
        with retry_context(max_attempts=3, operation_name="database_connect"):
            conn = connect_to_database()
            cursor = conn.cursor()
    """
    attempt = 1
    current_delay = delay

    while attempt <= max_attempts:
        try:
            # Si entramos aquí, el bloque se ejecutó sin excepciones
            yield
            return  # Salir exitosamente

        except exceptions as e:
            if attempt == max_attempts:
                logger.error(f"  {operation_name} falló después de {max_attempts} intentos: {e}")
                raise

            logger.warning(
                f"   {operation_name} falló (intento {attempt}/{max_attempts}). "
                f"Reintentando en {current_delay}s... Error: {e}"
            )

            time.sleep(current_delay)
            attempt += 1
            current_delay *= backoff
