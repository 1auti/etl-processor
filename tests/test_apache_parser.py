"""
Tests para el parser de Apache.
"""

from datetime import datetime

import pytest

from src.parsers.apache_parser import ApacheParser


class TestApacheParser:
    """Suite de tests para ApacheParser."""

    @pytest.fixture
    def parser(self):
        """Fixture que provee una instancia del parser."""
        return ApacheParser()

    def test_parse_valid_apache_common(self, parser):
        """Test: Parseo exitoso de formato Apache Common."""
        line = '192.168.1.100 - - [10/Jan/2026:14:23:45 +0000] "GET /api/users HTTP/1.1" 200 1523'

        result = parser.parse_line(line)

        assert result is not None
        assert result["ip"] == "192.168.1.100"
        assert result["method"] == "GET"
        assert result["url"] == "/api/users"
        assert result["status"] == 200
        assert result["bytes"] == 1523

    def test_parse_apache_combined_with_referrer(self, parser):
        """Test: Parseo de formato Combined con referrer y user-agent."""
        line = (
            "10.0.0.5 - - [28/Jan/2026:10:15:30 +0000] "
            '"POST /login HTTP/1.1" 302 0 '
            '"https://example.com/home" "Mozilla/5.0"'
        )

        result = parser.parse_line(line)

        assert result is not None
        assert result["method"] == "POST"
        assert result["referrer"] == "https://example.com/home"
        assert result["user_agent"] == "Mozilla/5.0"

    def test_parse_with_dash_bytes(self, parser):
        """Test: Manejo de '-' en campo bytes."""
        line = '172.16.0.1 - - [28/Jan/2026:11:00:00 +0000] "HEAD /health HTTP/1.1" 204 -'

        result = parser.parse_line(line)

        assert result is not None
        assert result["bytes"] == 0  # '-' se convierte a 0

    def test_parse_invalid_format(self, parser):
        """Test: Línea con formato inválido retorna None."""
        line = "esto no es un log válido"

        result = parser.parse_line(line)

        assert result is None

    def test_validate_valid_record(self, parser):
        """Test: Validación de registro correcto."""
        record = {
            "ip": "192.168.1.1",
            "timestamp": datetime.now(),
            "method": "GET",
            "url": "/test",
            "status": 200,
            "bytes": 100,
        }

        assert parser.validate_record(record) is True

    def test_validate_invalid_ip(self, parser):
        """Test: Rechazo de IP inválida."""
        record = {
            "ip": "999.999.999.999",  # IP inválida
            "timestamp": datetime.now(),
            "method": "GET",
            "url": "/test",
            "status": 200,
            "bytes": 100,
        }

        assert parser.validate_record(record) is False

    def test_validate_invalid_status(self, parser):
        """Test: Rechazo de status HTTP inválido."""
        record = {
            "ip": "192.168.1.1",
            "timestamp": datetime.now(),
            "method": "GET",
            "url": "/test",
            "status": 999,  # Status fuera de rango
            "bytes": 100,
        }

        assert parser.validate_record(record) is False
