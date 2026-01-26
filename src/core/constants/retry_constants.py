class RetryConstants:
    """Constantes para el sistema de reintentos."""

    # Configuración de reintentos
    DEFAULT_MAX_ATTEMPTS = 3
    DEFAULT_INITIAL_DELAY = 1.0      # segundos
    DEFAULT_BACKOFF_FACTOR = 2.0     # multiplicador exponencial
    DEFAULT_MAX_DELAY = 30.0         # delay máximo en segundos

    # Timeouts
    CONNECTION_RETRY_TIMEOUT = 5.0
    QUERY_RETRY_TIMEOUT = 10.0
    FILE_OPERATION_TIMEOUT = 3.0
