class PerformanceConstants:
    """Constantes relacionadas con performance."""

    # Thresholds de alerta
    SLOW_QUERY_THRESHOLD = 1.0  # segundos
    HIGH_ERROR_RATE_THRESHOLD = 0.1  # 10% de errores
    LOW_SUCCESS_RATE_THRESHOLD = 0.9  # 90% de éxito mínimo

    # Límites de procesamiento
    MAX_CONCURRENT_CONNECTIONS = 10
    MAX_QUEUE_SIZE = 10000
    PROCESSING_TIMEOUT = 300  # 5 minutos

    # Configuración de pools
    CONNECTION_POOL_MIN_SIZE = 2
    CONNECTION_POOL_MAX_SIZE = 10
    CONNECTION_POOL_TIMEOUT = 30
