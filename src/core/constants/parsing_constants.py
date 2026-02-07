class ParsingConstants:
    """Constantes para el parsing de logs."""

    # Formato de timestamp de Apache/Nginx
    APACHE_TIMESTAMP_FORMAT = "%d/%b/%Y:%H:%M:%S %z"

    # Formato alternativo sin timezone
    SIMPLE_TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"

    # Separadores comunes
    LOG_SEPARATOR = " "
    URL_QUERY_SEPARATOR = "?"
    URL_FRAGMENT_SEPARATOR = "#"

    # Límites de parsing
    MAX_LINE_LENGTH = 8192  # 8KB por línea de log
    MAX_ERRORS_TO_LOG = 5  # Mostrar solo primeros N errores

    # Patrones de IPs válidas
    IPV4_OCTETS = 4
    IPV4_MIN_VALUE = 0
    IPV4_MAX_VALUE = 255
