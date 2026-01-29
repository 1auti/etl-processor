from typing import Any, Dict

import structlog


class MetricsLogger:
    """
    Helper para loguear métricas de forma estructurada.
    """

    def __init__(self, logger: structlog.BoundLogger):
        self.logger = logger

    def log_counter(self, name: str, value: int, **labels):
        """Loguea un contador (ej: registros procesados)."""
        self.logger.info(
            "metric.counter", metric_name=name, value=value, metric_type="counter", **labels
        )

    def log_gauge(self, name: str, value: float, **labels):
        """Loguea un gauge (ej: memoria usada)."""
        self.logger.info(
            "metric.gauge", metric_name=name, value=value, metric_type="gauge", **labels
        )

    def log_histogram(self, name: str, value: float, **labels):
        """Loguea un histogram (ej: latencia)."""
        self.logger.info(
            "metric.histogram", metric_name=name, value=value, metric_type="histogram", **labels
        )

    def log_processing_stats(self, stats: Dict[str, Any]):
        """Loguea estadísticas de procesamiento."""
        self.logger.info("processing.stats", **stats)
