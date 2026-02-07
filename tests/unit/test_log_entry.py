"""
Tests completos para LogEntry.
"""

from datetime import datetime

import pytest
from pydantic import ValidationError

from src.models import HTTPMethod, LogEntry


class TestLogEntryCreation:
    """Tests de creación de LogEntry."""

    def test_create_valid_log_entry(self, valid_log_record):
        """Test creación de LogEntry válido."""
        log = LogEntry.from_log_record(valid_log_record)

        assert log.ip_address == "192.168.1.1"
        assert log.method == "GET"
        assert log.status_code == 200
        assert log.response_size == 1234

    def test_create_with_minimal_fields(self):
        """Test creación con campos mínimos requeridos."""
        log = LogEntry(
            ip_address="10.0.0.1",
            timestamp=datetime.now(),
            method="POST",
            endpoint="/api/test",
            status_code=201,
            response_size=512,
        )

        assert log.ip_address == "10.0.0.1"
        assert log.http_version == "HTTP/1.1"  # Default

    def test_create_with_optional_fields(self):
        """Test creación con campos opcionales."""
        log = LogEntry(
            ip_address="192.168.1.1",
            timestamp=datetime.now(),
            method="GET",
            endpoint="/test",
            status_code=200,
            response_size=100,
            user_agent="Mozilla/5.0",
            referer="https://example.com",
            remote_user="admin",
            request_time=0.05,
        )

        assert log.user_agent == "Mozilla/5.0"
        assert log.referer == "https://example.com"
        assert log.remote_user == "admin"
        assert log.request_time == 0.05


class TestLogEntryValidation:
    """Tests de validación de LogEntry."""

    def test_invalid_ip_raises_error(self, invalid_log_records):
        """Test que IP inválida levanta ValidationError."""
        with pytest.raises(ValidationError, match="IP inválida"):
            LogEntry.from_log_record(invalid_log_records["invalid_ip"])

    def test_invalid_http_method_raises_error(self, invalid_log_records):
        """Test que método HTTP inválido levanta error."""
        with pytest.raises(ValidationError, match="Método HTTP inválido"):
            LogEntry.from_log_record(invalid_log_records["invalid_method"])

    def test_invalid_status_code_raises_error(self, invalid_log_records):
        """Test que status code inválido levanta error."""
        with pytest.raises(ValidationError):
            LogEntry.from_log_record(invalid_log_records["invalid_status_code"])

    def test_suspicious_endpoint_raises_error(self, invalid_log_records):
        """Test que endpoint con XSS levanta error."""
        with pytest.raises(ValidationError, match="sospechoso"):
            LogEntry.from_log_record(invalid_log_records["suspicious_endpoint"])

    def test_negative_response_size_raises_error(self, invalid_log_records):
        """Test que response_size negativo levanta error."""
        with pytest.raises(ValidationError):
            LogEntry.from_log_record(invalid_log_records["negative_response_size"])

    def test_endpoint_must_start_with_slash(self):
        """Test que endpoint debe comenzar con /."""
        with pytest.raises(ValidationError, match="comenzar con /"):
            LogEntry(
                ip_address="192.168.1.1",
                timestamp=datetime.now(),
                method="GET",
                endpoint="api/test",  # Sin /
                status_code=200,
                response_size=100,
            )

    def test_http_version_pattern_validation(self):
        """Test validación de patrón HTTP version."""
        with pytest.raises(ValidationError):
            LogEntry(
                ip_address="192.168.1.1",
                timestamp=datetime.now(),
                method="GET",
                endpoint="/test",
                status_code=200,
                response_size=100,
                http_version="HTTP/INVALID",  # Patrón inválido
            )

    def test_method_normalization(self):
        """Test que método se normaliza a uppercase."""
        log = LogEntry(
            ip_address="192.168.1.1",
            timestamp=datetime.now(),
            method="get",  # Lowercase
            endpoint="/test",
            status_code=200,
            response_size=100,
        )

        assert log.method == "GET"  # Normalizado a uppercase


class TestLogEntryProperties:
    """Tests de propiedades de LogEntry."""

    def test_is_success_property(self):
        """Test propiedad is_success."""
        log = LogEntry(
            ip_address="192.168.1.1",
            timestamp=datetime.now(),
            method="GET",
            endpoint="/test",
            status_code=200,
            response_size=100,
        )

        assert log.is_success is True
        assert log.is_error is False
        assert log.get_status_category() == "success"

    def test_is_client_error_property(self):
        """Test propiedad is_client_error."""
        log = LogEntry(
            ip_address="192.168.1.1",
            timestamp=datetime.now(),
            method="GET",
            endpoint="/not-found",
            status_code=404,
            response_size=50,
        )

        assert log.is_client_error is True
        assert log.is_error is True
        assert log.is_success is False
        assert log.get_status_category() == "client_error"

    def test_is_server_error_property(self):
        """Test propiedad is_server_error."""
        log = LogEntry(
            ip_address="192.168.1.1",
            timestamp=datetime.now(),
            method="POST",
            endpoint="/api/crash",
            status_code=500,
            response_size=100,
        )

        assert log.is_server_error is True
        assert log.is_error is True
        assert log.get_status_category() == "server_error"

    def test_is_redirect_property(self):
        """Test propiedad is_redirect."""
        log = LogEntry(
            ip_address="192.168.1.1",
            timestamp=datetime.now(),
            method="GET",
            endpoint="/old-page",
            status_code=301,
            response_size=0,
        )

        assert log.is_redirect is True
        assert log.get_status_category() == "redirection"

    def test_is_informational_property(self):
        """Test propiedad is_informational."""
        log = LogEntry(
            ip_address="192.168.1.1",
            timestamp=datetime.now(),
            method="GET",
            endpoint="/test",
            status_code=100,
            response_size=0,
        )

        assert log.is_informational is True
        assert log.get_status_category() == "informational"

    def test_get_method_category(self):
        """Test categorización de método HTTP."""
        read_log = LogEntry(
            ip_address="192.168.1.1",
            timestamp=datetime.now(),
            method="GET",
            endpoint="/test",
            status_code=200,
            response_size=100,
        )

        write_log = LogEntry(
            ip_address="192.168.1.1",
            timestamp=datetime.now(),
            method="POST",
            endpoint="/test",
            status_code=201,
            response_size=50,
        )

        assert read_log.get_method_category() == "read"
        assert write_log.get_method_category() == "write"


class TestLogEntryConversions:
    """Tests de conversiones de LogEntry."""

    def test_to_log_record_conversion(self, valid_log_record):
        """Test conversión a LogRecord."""
        log = LogEntry.from_log_record(valid_log_record)
        record = log.to_log_record()

        assert isinstance(record, dict)
        assert record["ip_address"] == valid_log_record["ip_address"]
        assert record["method"] == valid_log_record["method"]
        assert record["status_code"] == valid_log_record["status_code"]

    def test_round_trip_conversion(self, valid_log_record):
        """Test conversión ida y vuelta."""
        # Dict -> Model -> Dict
        log = LogEntry.from_log_record(valid_log_record)
        record_back = log.to_log_record()
        log_again = LogEntry.from_log_record(record_back)

        assert log.ip_address == log_again.ip_address
        assert log.method == log_again.method
        assert log.status_code == log_again.status_code

    def test_to_json_conversion(self, valid_log_record):
        """Test conversión a JSON."""
        log = LogEntry.from_log_record(valid_log_record)
        json_str = log.to_json()

        assert isinstance(json_str, str)
        assert "192.168.1.1" in json_str
        assert '"method":"GET"' in json_str


class TestLogEntrySuspiciousPatterns:
    """Tests de detección de patrones sospechosos."""

    @pytest.mark.parametrize(
        "suspicious_endpoint,pattern",
        [
            ("/test?query=../../../etc/passwd", ".."),
            ("/api?exec=<script>alert('xss')</script>", "<script"),
            ("/page?code=javascript:alert(1)", "javascript:"),
            ("/search?q='; DROP TABLE users;--", ";--"),
            ("/admin?cmd=DROP TABLE logs", "DROP TABLE"),
            ("/api?union=UNION SELECT * FROM passwords", "UNION SELECT"),
        ],
    )
    def test_suspicious_patterns_detected(self, suspicious_endpoint, pattern):
        """Test que patrones sospechosos son detectados."""
        with pytest.raises(ValidationError, match="sospechoso"):
            LogEntry(
                ip_address="192.168.1.1",
                timestamp=datetime.now(),
                method="GET",
                endpoint=suspicious_endpoint,
                status_code=200,
                response_size=100,
            )
