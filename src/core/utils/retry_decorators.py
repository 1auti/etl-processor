import functools
import logging
import random
import time
from typing import Any, Callable, Optional, Tuple, Type

logger = logging.getLogger(__name__)


def retry_advanced(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    jitter: float = 0.1,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable[[int, Exception, float], None]] = None,
    on_failure: Optional[Callable[[Exception], None]] = None,
    on_success: Optional[Callable[[Any, float], None]] = None,
    timeout: Optional[float] = None,
    retry_predicate: Optional[Callable[[Exception], bool]] = None,
):
    """
    Decorador avanzado para reintentos automáticos con características empresariales.

    Args:
        max_attempts: Número máximo de intentos
        initial_delay: Delay inicial en segundos
        max_delay: Delay máximo permitido (para evitar esperas infinitas)
        backoff_factor: Factor de multiplicación del delay
        jitter: Aleatoriedad para evitar thundering herd problem
        exceptions: Excepciones que activan el reintento
        on_retry: Callback ejecutado en cada reintento (intento, error, next_delay)
        on_failure: Callback ejecutado cuando todos los intentos fallan
        on_success: Callback ejecutado al éxito (resultado, total_duration)
        timeout: Tiempo máximo total de ejecución
        retry_predicate: Función que decide si se debe reintentar basado en la excepción

    Returns:
        Decorador de función
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            attempt = 1
            current_delay = initial_delay

            while attempt <= max_attempts:
                try:
                    # Verificar timeout global
                    if timeout and (time.time() - start_time) > timeout:
                        raise TimeoutError(f"Timeout global de {timeout}s excedido")

                    # Intentar ejecutar la función
                    result = func(*args, **kwargs)

                    # Ejecutar callback de éxito si existe
                    if on_success:
                        try:
                            duration = time.time() - start_time
                            on_success(result, duration)
                        except Exception as e:
                            logger.warning(f"Error en on_success callback: {e}")

                    return result

                except exceptions as e:
                    # Verificar si debemos reintentar basado en el predicado
                    if retry_predicate and not retry_predicate(e):
                        logger.info(f"No se reintenta {func.__name__}: {e}")
                        raise

                    # Último intento fallido
                    if attempt == max_attempts:
                        logger.error(
                            f" {func.__name__} falló definitivamente después de {max_attempts} intentos. "
                            f"Duración total: {time.time() - start_time:.2f}s. Error: {type(e).__name__}: {e}"
                        )

                        # Ejecutar callback de fallo
                        if on_failure:
                            try:
                                on_failure(e)
                            except Exception as callback_error:
                                logger.error(f"Error en on_failure callback: {callback_error}")

                        raise

                    # Calcular próximo delay con jitter
                    jitter_amount = current_delay * jitter
                    actual_delay = current_delay + (jitter_amount * (2 * random.random() - 1))
                    actual_delay = max(0.1, min(actual_delay, max_delay))

                    # Log del reintento
                    logger.warning(
                        f"  {func.__name__} falló en intento {attempt}/{max_attempts}. "
                        f"Reintentando en {actual_delay:.1f}s... "
                        f"Error: {type(e).__name__}: {e}"
                    )

                    # Ejecutar callback de reintento
                    if on_retry:
                        try:
                            on_retry(attempt, e, actual_delay)
                        except Exception as callback_error:
                            logger.error(f"Error en on_retry callback: {callback_error}")

                    # Esperar antes del siguiente intento
                    time.sleep(actual_delay)

                    # Actualizar para próximo intento
                    attempt += 1
                    current_delay = min(current_delay * backoff_factor, max_delay)

                except Exception as e:
                    # Capturar cualquier otra excepción no esperada
                    logger.error(f" Error inesperado en {func.__name__}: {type(e).__name__}: {e}")
                    raise

        return wrapper

    return decorator
