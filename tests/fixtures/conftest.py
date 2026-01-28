"""
Fixtures globales de pytest para todos los tests
"""

import pytest

from src.core.logger import configure_logging


def setup_logging():
    "Configura loggin para test"


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
