
class LoggingConstants:
    """Constantes para el sistema de logging."""

    # Formatos de log
    DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    DETAILED_LOG_FORMAT = "%(asctime)s - %(name)s - [%(levelname)s] - %(filename)s:%(lineno)d - %(message)s"
    SIMPLE_LOG_FORMAT = "%(levelname)s - %(message)s"

    # Formato de fecha
    DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    ISO_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"

    # Niveles de log (en orden de severidad)
    LEVEL_DEBUG = "DEBUG"
    LEVEL_INFO = "INFO"
    LEVEL_WARNING = "WARNING"
    LEVEL_ERROR = "ERROR"
    LEVEL_CRITICAL = "CRITICAL"

    # Configuración de archivos
    MAX_LOG_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    LOG_BACKUP_COUNT = 5
    DEFAULT_LOG_DIR = "logs"
