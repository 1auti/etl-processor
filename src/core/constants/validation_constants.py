class ValidationConstants:
    """Constantes para validaciones."""

    # Rangos válidos
    MIN_STATUS_CODE = 100
    MAX_STATUS_CODE = 599
    MIN_BYTES = 0
    MAX_BYTES = 2147483647      # MAX INT en PostgreSQL

    # Límites de datos
    MIN_BATCH_SIZE = 1
    MAX_RECORDS_PER_FILE = 1_000_000

    # Patrones comunes
    LOCALHOST_IPS = {'127.0.0.1', '::1', 'localhost'}
    PRIVATE_IP_RANGES = {
        '10.',      # 10.0.0.0/8
        '172.16.',  # 172.16.0.0/12
        '192.168.'  # 192.168.0.0/16
    }
