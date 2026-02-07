"""
Fixtures globales de pytest para todos los tests.
"""

from datetime import datetime
from typing import Any, Dict

import pytest

from src.core.abstractions.types import ProcessingStatus
from src.core.config import Config
from src.core.logger import configure_logging


@pytest.fixture(scope="session")
def test_config():
    """Config para ambiente de testing."""
    return Config(env="test")


@pytest.fixture(scope="session", autouse=True)
def setup_logging():
    """Configura logging para tests."""
    configure_logging(log_level="DEBUG")


@pytest.fixture
def sample_log_lines():
    """Fixture con líneas de log de ejemplo."""
    return [
        '192.168.1.1 - - [01/Jan/2024:12:00:00 +0000] "GET /index.html HTTP/1.1" 200 1234',
        '10.0.0.1 - - [01/Jan/2024:12:00:01 +0000] "POST /api/login HTTP/1.1" 401 567',
    ]


@pytest.fixture
def temp_log_file(tmp_path):
    """Crea un archivo de log temporal para tests."""
    log_file = tmp_path / "test.log"
    log_file.write_text("test log content\n")
    return log_file


@pytest.fixture
def valid_log_record() -> Dict[str, Any]:
    """
    Fixture con un LogRecord válido.
    Representa el output típico de un parser.
    """
    return {
        "ip_address": "192.168.1.1",
        "timestamp": datetime(2024, 1, 15, 10, 30, 0),
        "method": "GET",
        "endpoint": "/api/users",
        "status_code": 200,
        "response_size": 1234,
        "http_version": "HTTP/1.1",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "referer": "https://example.com",
        "remote_user": None,
        "request_time": 0.025,
    }


@pytest.fixture
def invalid_log_records() -> Dict[str, Dict[str, Any]]:
    """Fixture con LogRecords inválidos para tests negativos."""
    return {
        "invalid_ip": {
            "ip_address": "999.999.999.999",  # IP inválida
            "timestamp": datetime.now(),
            "method": "GET",
            "endpoint": "/test",
            "status_code": 200,
            "response_size": 100,
            "http_version": "HTTP/1.1",
        },
        "invalid_method": {
            "ip_address": "192.168.1.1",
            "timestamp": datetime.now(),
            "method": "INVALID_METHOD",  # Método inválido
            "endpoint": "/test",
            "status_code": 200,
            "response_size": 100,
            "http_version": "HTTP/1.1",
        },
        "invalid_status_code": {
            "ip_address": "192.168.1.1",
            "timestamp": datetime.now(),
            "method": "GET",
            "endpoint": "/test",
            "status_code": 999,  # Status code inválido
            "response_size": 100,
            "http_version": "HTTP/1.1",
        },
        "suspicious_endpoint": {
            "ip_address": "192.168.1.1",
            "timestamp": datetime.now(),
            "method": "GET",
            "endpoint": '/test?query=<script>alert("xss")</script>',  # XSS
            "status_code": 200,
            "response_size": 100,
            "http_version": "HTTP/1.1",
        },
        "negative_response_size": {
            "ip_address": "192.168.1.1",
            "timestamp": datetime.now(),
            "method": "GET",
            "endpoint": "/test",
            "status_code": 200,
            "response_size": -100,  # Negativo
            "http_version": "HTTP/1.1",
        },
    }


@pytest.fixture
def sample_apache_log_lines() -> list[str]:
    """Fixture con líneas de log Apache para parsers."""
    return [
        '192.168.1.1 - - [15/Jan/2024:10:30:00 +0000] "GET /api/users HTTP/1.1" 200 1234',
        '10.0.0.1 - admin [15/Jan/2024:10:30:01 +0000] "POST /api/login HTTP/1.1" 401 567',
        '172.16.0.1 - - [15/Jan/2024:10:30:02 +0000] "DELETE /api/resource/123 HTTP/1.1" 204 0',
    ]


@pytest.fixture
def processing_result_data() -> Dict[str, Any]:
    """Fixture con datos de resultado de procesamiento."""

    return {
        "success": True,
        "records_processed": 1000,
        "errors": 5,
        "duration_seconds": 12.5,
        "status": ProcessingStatus.COMPLETED,
        "message": "Procesamiento completado exitosamente",
        "details": {"source": "test_file.log", "batch_size": 100},
    }
