

# ========== CONSTANTES DE MÉTRICAS ==========

class MetricsConstants:
    """Constantes para el sistema de métricas."""
    
    # Nombres de métricas estándar
    METRIC_LINES_EXTRACTED = "etl.lines_extracted"
    METRIC_RECORDS_PARSED = "etl.records_parsed"
    METRIC_PARSE_ERRORS = "etl.parse_errors"
    METRIC_RECORDS_INSERTED = "etl.records_inserted"
    METRIC_PARSE_SUCCESS_RATE = "etl.parse_success_rate"
    METRIC_PROCESSING_TIME = "etl.processing_time"
    METRIC_DB_CONNECTIONS = "db.active_connections"
    METRIC_QUERY_DURATION = "db.query_duration"

    # Configuración de métricas
    DEFAULT_METRICS_BATCH_SIZE = 50
    METRICS_FLUSH_INTERVAL = 60      # segundos

    # Tags comunes
    TAG_COMPONENT = "component"
    TAG_STATUS = "status"
    TAG_SOURCE = "source"
    TAG_DATABASE = "database"
