# tests/test_example_usage.py
import pytest
from unittest.mock import patch, MagicMock

from src.core.logger import (
    configuration_structlog,
    context_manager_logger,
    decorador_logging,
    logger_factory,
    metrics_logger,
    log_context,
    get_logger,
    configure_logging,
    log_function_call,
    MetricsLogger
)

class TestExampleUsage:

    def test_context_manager_usage(self):
        """Test específico del context manager"""


        configure_logging(log_level="INFO", json_logs=False)
        logger = get_logger(__name__)

        # Mock del logger para verificar llamadas
        with patch.object(logger, 'info') as mock_info:
            with log_context(request_id="abc-123", user="john"):
                logger.info("Inside context")

            # Verificar que se llamó con los parámetros correctos
            mock_info.assert_called()

    def test_function_decorator(self):
        """Test del decorador log_function_call"""


        configure_logging(log_level="INFO", json_logs=False)
        logger = get_logger(__name__)

        @log_function_call(logger)
        def multiply(a, b):
            return a * b

        # Test que la función funciona correctamente
        result = multiply(3, 4)
        assert result == 12

    def test_metrics_logger(self):
        """Test de MetricsLogger"""
        

        configure_logging(log_level="INFO", json_logs=False)
        logger = get_logger(__name__)

        metrics = MetricsLogger(logger)

        # Verificar que no hay errores al llamar métricas
        metrics.log_counter("test_counter", 1)
        metrics.log_gauge("test_gauge", 100.5)
        metrics.log_histogram("test_histogram", 45.2)
