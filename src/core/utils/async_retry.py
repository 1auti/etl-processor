import asyncio
import functools
from typing import Callable, Optional, Tuple, Type

from core import logger


def async_retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable[[int, Exception, float], None]] = None
):
    """
    Decorador de reintentos para funciones asíncronas.

    Args:
        max_attempts: Número máximo de intentos
        delay: Delay inicial en segundos
        backoff: Factor de multiplicación del delay
        exceptions: Excepciones que activan el reintento
        on_retry: Callback ejecutado en cada reintento

    Returns:
        Decorador para funciones async
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            attempt = 1
            current_delay = delay

            while attempt <= max_attempts:
                try:
                    return await func(*args, **kwargs)

                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error(
                            f" {func.__name__} falló después de {max_attempts} intentos async: {e}"
                        )
                        raise

                    logger.warning(
                        f"  {func.__name__} falló (intento {attempt}/{max_attempts}). "
                        f"Reintentando en {current_delay}s... Error: {e}"
                    )

                    if on_retry:
                        try:
                            on_retry(attempt, e, current_delay)
                        except Exception as callback_error:
                            logger.error(f"Error en on_retry callback: {callback_error}")

                    # Espera asíncrona
                    await asyncio.sleep(current_delay)

                    attempt += 1
                    current_delay *= backoff

            # Nunca debería llegar aquí
            raise RuntimeError("Lógica de reintentos falló")

        return wrapper
    return decorator
