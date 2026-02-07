# ========== CONSTANTES DE BASE DE DATOS ==========


class DatabaseConstants:
    """Constantes relacionadas con la base de datos."""

    # Nombres de tablas
    TABLE_WEB_LOGS = "web_logs"
    TABLE_METRICS = "metrics"

    # Tamaños de campos
    MAX_IP_LENGTH = 45  # IPv6 puede ser hasta 45 caracteres
    MAX_METHOD_LENGTH = 10  # Métodos HTTP más largos
    MAX_URL_LENGTH = 500  # URLs largas pero razonables
    MAX_METRIC_NAME_LENGTH = 255

    # Configuración de conexión
    DEFAULT_PORT = 5432
    DEFAULT_HOST = "localhost"
    CONNECTION_TIMEOUT = 30  # segundos
    QUERY_TIMEOUT = 60  # segundos

    # Configuración de batches
    DEFAULT_BATCH_SIZE = 1000
    MIN_BATCH_SIZE = 100
    MAX_BATCH_SIZE = 10000
