
from pathlib import Path
import logging
import sys
import structlog
from structlog.stdlib import LoggerFactory
from src.core.logger.logger_procesadores import add_caller_info, add_log_level, add_timestamp



def configure_logging(
    log_level: str = "INFO",
    log_file: Path = None,
    json_logs: bool = True
):
    """
    Configura el sistema de logging estructurado.

    Args:
        log_level: Nivel de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Ruta del archivo de log (opcional)
        json_logs: Si True, logs en formato JSON; si False, formato human-readable
    """

    # Configurar logging estándar de Python
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper())
    )

    # Procesadores comunes
    processors = [
        structlog.contextvars.merge_contextvars,  # Merge context vars
        add_log_level,                             # Agregar nivel
        add_timestamp,                             # Agregar timestamp
        add_caller_info,                           # Agregar caller info
        structlog.processors.StackInfoRenderer(),  # Stack info en errores
        structlog.processors.format_exc_info,      # Formatear excepciones
    ]

    # Procesador final según formato
    if json_logs:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))

    # Configurar structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Si hay archivo de log, configurar handler
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, log_level.upper()))

        # Formato del archivo
        if json_logs:
            formatter = logging.Formatter('%(message)s')
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )

        file_handler.setFormatter(formatter)
        logging.root.addHandler(file_handler)
