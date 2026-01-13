
# tests/test_logging_example.py
import sys
from io import StringIO
import json
from contextlib import redirect_stdout, redirect_stderr
import pytest

def test_example_usage():
    """Test del ejemplo de uso del sistema de logging"""

    # Capturar stdout para verificar logs
    captured_output = StringIO()

    # Importar el módulo de logging
    from your_module import (
        configure_logging,
        get_logger,
        log_context,
        log_function_call,
        MetricsLogger
    )

    # Configurar logging (capturando output)
    with redirect_stdout(captured_output), redirect_stderr(captured_output):
        configure_logging(
            log_level="DEBUG",
            json_logs=False
        )

        # Obtener logger
        logger = get_logger(__name__)

        # Verificar que se pueden hacer logs sin errores
        logger.debug("This is a debug message")
        logger.info("Processing started", file="sample.log", lines=1000)

        # Test context manager
        with log_context(request_id="abc-123", user="john"):
            logger.info("Inside context")

        # Test decorador
        @log_function_call(logger)
        def example_function(x, y):
            return x + y

        result = example_function(5, 3)
        assert result == 8

        # Test métricas
        metrics = MetricsLogger(logger)
        metrics.log_counter("lines_processed", 5000, status="success")
        metrics.log_gauge("memory_usage_mb", 256.5)

    # Verificar que se generó output (logs)
    output = captured_output.getvalue()
    assert output  # Debería haber algo de output

    # Verificar que ciertas palabras clave están en los logs
    assert "debug" in output.lower()
    assert "processing started" in output.lower()
