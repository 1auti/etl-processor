"""
Tests para el parser de Nginx.

Cubre:
- Parseo de logs válidos en diferentes formatos
- Manejo de campos opcionales (request_time, upstream_time)
- Validación de registros
- Casos edge: requests malformados, bytes "-", IPv6
"""

from datetime import datetime

import pytest

from src.parsers.nginx_parser import NginxParser


class TestNginxParser:
    """Suite de tests para NginxParser."""

    @pytest.fixture
    def parser(self):
        """Fixture que provee una instancia del parser."""
        return NginxParser()

    # ==========================================
    # TESTS DE PARSEO EXITOSO
    # ==========================================

    def test_parse_valid_nginx_combined(self, parser):
        """Test: Parseo exitoso de formato Nginx Combined básico."""
        line = (
            "172.16.254.1 - - [29/Jan/2026:08:15:32 +0000] "
            '"GET /api/v1/users HTTP/1.1" 200 2341 "-" "curl/7.68.0"'
        )

        result = parser.parse_line(line)

        assert result is not None
        assert result["ip"] == "172.16.254.1"
        assert result["user"] == "-"
        assert result["method"] == "GET"
        assert result["url"] == "/api/v1/users"
        assert result["status"] == 200
        assert result["bytes"] == 2341
        assert result["user_agent"] == "curl/7.68.0"

    def test_parse_with_authenticated_user(self, parser):
        """Test: Parseo con usuario autenticado (no "-")."""
        line = (
            "10.0.0.5 - admin [29/Jan/2026:10:30:00 +0000] "
            '"POST /admin/users HTTP/1.1" 201 156 '
            '"https://admin.example.com" "Mozilla/5.0"'
        )

        result = parser.parse_line(line)

        assert result is not None
        assert result["user"] == "admin"
        assert result["method"] == "POST"
        assert result["referrer"] == "https://admin.example.com"

    def test_parse_with_request_time(self, parser):
        """Test: Parseo con request_time (campo opcional)."""
        line = (
            "192.168.1.100 - - [29/Jan/2026:12:00:00 +0000] "
            '"GET /slow-endpoint HTTP/1.1" 200 5000 "-" "python-requests/2.28" 0.523'
        )

        result = parser.parse_line(line)

        assert result is not None
        assert "request_time" in result
        assert result["request_time"] == 0.523

    def test_parse_with_request_and_upstream_time(self, parser):
        """Test: Parseo con request_time y upstream_time."""
        line = (
            "10.20.30.40 - - [29/Jan/2026:14:45:00 +0000] "
            '"POST /api/proxy HTTP/1.1" 200 1024 "-" "Go-http-client/1.1" 1.234 0.987'
        )

        result = parser.parse_line(line)

        assert result is not None
        assert result["request_time"] == 1.234
        assert result["upstream_time"] == 0.987

    def test_parse_with_dash_upstream_time(self, parser):
        """Test: upstream_time puede ser "-" (sin upstream)."""
        line = (
            "10.0.0.1 - - [29/Jan/2026:15:00:00 +0000] "
            '"GET /static/logo.png HTTP/1.1" 200 8192 "-" "Mozilla/5.0" 0.001 -'
        )

        result = parser.parse_line(line)

        assert result is not None
        assert result["request_time"] == 0.001
        assert "upstream_time" not in result  # "-" se convierte a None y no se agrega

    def test_parse_with_dash_bytes(self, parser):
        """Test: Manejo de "-" en campo bytes (ej: HEAD requests)."""
        line = (
            "192.168.1.1 - - [29/Jan/2026:16:00:00 +0000] "
            '"HEAD /health HTTP/1.1" 204 - "-" "Kubernetes-Probe/1.0"'
        )

        result = parser.parse_line(line)

        assert result is not None
        assert result["bytes"] == 0  # "-" se convierte a 0

    def test_parse_ipv6_address(self, parser):
        """Test: Parseo de dirección IPv6."""
        line = (
            "2001:0db8:85a3::8a2e:0370:7334 - - [29/Jan/2026:17:00:00 +0000] "
            '"GET /ipv6-test HTTP/1.1" 200 100 "-" "curl/7.68.0"'
        )

        result = parser.parse_line(line)

        assert result is not None
        assert result["ip"] == "2001:0db8:85a3::8a2e:0370:7334"

    # ==========================================
    # TESTS DE CASOS EDGE Y REQUESTS MALFORMADOS
    # ==========================================

    def test_parse_empty_request(self, parser):
        """Test: Request vacío debe retornar None."""
        line = "10.0.0.1 - - [29/Jan/2026:19:00:00 +0000] " '"" 400 0 "-" "-"'

        result = parser.parse_line(line)

        assert result is None  # Request vacío es inválido

    def test_parse_malformed_request_only_method(self, parser):
        """Test: Request con solo método (sin URL) es inválido."""
        line = "10.0.0.1 - - [29/Jan/2026:20:00:00 +0000] " '"GET" 400 0 "-" "-"'

        result = parser.parse_line(line)

        assert result is None  # Debe tener al menos METHOD + URL

    # ==========================================
    # TESTS DE FORMATO INVÁLIDO
    # ==========================================

    def test_parse_invalid_format(self, parser):
        """Test: Línea con formato completamente inválido."""
        line = "esto no es un log válido de ningún tipo"

        result = parser.parse_line(line)

        assert result is None

    def test_parse_line_too_long(self, parser):
        """Test: Línea excesivamente larga debe ser rechazada."""
        # Crear una línea muy larga (>8KB)
        long_url = "x" * 10000
        line = (
            f"10.0.0.1 - - [29/Jan/2026:22:00:00 +0000] "
            f'"GET /{long_url} HTTP/1.1" 414 0 "-" "-"'
        )

        result = parser.parse_line(line)

        assert result is None  # Debe rechazar por exceder MAX_LINE_LENGTH

    # ==========================================
    # TESTS DE VALIDACIÓN DE REGISTROS
    # ==========================================

    def test_validate_valid_record(self, parser):
        """Test: Validación de registro completamente válido."""
        record = {
            "ip": "192.168.1.1",
            "user": "-",
            "timestamp": datetime.now(),
            "method": "GET",
            "url": "/api/test",
            "status": 200,
            "bytes": 1024,
            "referrer": None,
            "user_agent": "curl/7.68.0",
        }

        assert parser.validate_record(record) is True

    def test_validate_record_with_optional_fields(self, parser):
        """Test: Validación con campos opcionales."""
        record = {
            "ip": "10.0.0.1",
            "user": "admin",
            "timestamp": datetime.now(),
            "method": "POST",
            "url": "/api/users",
            "status": 201,
            "bytes": 512,
            "referrer": "https://example.com",
            "user_agent": "Mozilla/5.0",
            "request_time": 0.123,
            "upstream_time": 0.045,
        }

        assert parser.validate_record(record) is True

    def test_validate_missing_required_field(self, parser):
        """Test: Rechazo de registro sin campo requerido."""
        record = {
            "ip": "192.168.1.1",
            # Falta 'timestamp'
            "method": "GET",
            "url": "/test",
            "status": 200,
            "bytes": 100,
        }

        assert parser.validate_record(record) is False

    def test_validate_invalid_ipv4(self, parser):
        """Test: Rechazo de IPv4 inválido."""
        record = {
            "ip": "999.999.999.999",  # Octetos fuera de rango
            "user": "-",
            "timestamp": datetime.now(),
            "method": "GET",
            "url": "/test",
            "status": 200,
            "bytes": 100,
        }

        assert parser.validate_record(record) is False

    def test_validate_invalid_http_status(self, parser):
        """Test: Rechazo de status HTTP fuera de rango."""
        record = {
            "ip": "192.168.1.1",
            "user": "-",
            "timestamp": datetime.now(),
            "method": "GET",
            "url": "/test",
            "status": 999,  # Status inválido
            "bytes": 100,
        }

        assert parser.validate_record(record) is False

    def test_validate_negative_bytes(self, parser):
        """Test: Rechazo de bytes negativo."""
        record = {
            "ip": "192.168.1.1",
            "user": "-",
            "timestamp": datetime.now(),
            "method": "GET",
            "url": "/test",
            "status": 200,
            "bytes": -100,  # Bytes negativo
        }

        assert parser.validate_record(record) is False

    def test_validate_invalid_http_method(self, parser):
        """Test: Rechazo de método HTTP desconocido."""
        record = {
            "ip": "192.168.1.1",
            "user": "-",
            "timestamp": datetime.now(),
            "method": "INVALID",  # Método no estándar
            "url": "/test",
            "status": 200,
            "bytes": 100,
        }

        assert parser.validate_record(record) is False

    def test_validate_empty_url(self, parser):
        """Test: Rechazo de URL vacía."""
        record = {
            "ip": "192.168.1.1",
            "user": "-",
            "timestamp": datetime.now(),
            "method": "GET",
            "url": "",  # URL vacía
            "status": 200,
            "bytes": 100,
        }

        assert parser.validate_record(record) is False

    def test_validate_negative_request_time(self, parser):
        """Test: Rechazo de request_time negativo."""
        record = {
            "ip": "192.168.1.1",
            "user": "-",
            "timestamp": datetime.now(),
            "method": "GET",
            "url": "/test",
            "status": 200,
            "bytes": 100,
            "request_time": -0.5,  # Tiempo negativo
        }

        assert parser.validate_record(record) is False

    # ==========================================
    # TESTS DE MÉTODOS AUXILIARES
    # ==========================================

    def test_parse_request_normal(self, parser):
        """Test: Parseo de request normal."""
        method, url = parser._parse_request("GET /api/users HTTP/1.1")

        assert method == "GET"
        assert url == "/api/users"

    def test_parse_request_without_version(self, parser):
        """Test: Parseo de request sin versión HTTP."""
        method, url = parser._parse_request("POST /login")

        assert method == "POST"
        assert url == "/login"

    def test_parse_request_empty(self, parser):
        """Test: Request vacío retorna None, None."""
        method, url = parser._parse_request("")

        assert method is None
        assert url is None

    def test_parse_request_only_method(self, parser):
        """Test: Request con solo método es inválido."""
        method, url = parser._parse_request("GET")

        assert method is None
        assert url is None

    def test_parse_float_or_none_valid(self, parser):
        """Test: Conversión válida de string a float."""
        result = parser._parse_float_or_none("0.123")

        assert result == 0.123

    def test_parse_float_or_none_dash(self, parser):
        """Test: "-" se convierte a None."""
        result = parser._parse_float_or_none("-")

        assert result is None

    def test_parse_float_or_none_none(self, parser):
        """Test: None permanece como None."""
        result = parser._parse_float_or_none(None)

        assert result is None

    def test_parse_float_or_none_invalid(self, parser):
        """Test: String inválido retorna None."""
        result = parser._parse_float_or_none("invalid")

        assert result is None

    def test_is_valid_ipv4_valid(self, parser):
        """Test: Validación de IPv4 correcto."""
        assert parser._is_valid_ipv4("192.168.1.1") is True
        assert parser._is_valid_ipv4("10.0.0.1") is True
        assert parser._is_valid_ipv4("172.16.254.1") is True

    def test_is_valid_ipv4_invalid(self, parser):
        """Test: Rechazo de IPv4 inválido."""
        assert parser._is_valid_ipv4("256.1.1.1") is False
        assert parser._is_valid_ipv4("192.168.1") is False
        assert parser._is_valid_ipv4("192.168.1.1.1") is False
        assert parser._is_valid_ipv4("abc.def.ghi.jkl") is False

    def test_is_valid_ipv6_valid(self, parser):
        """Test: Validación de IPv6 correcto (simplificada)."""
        assert parser._is_valid_ipv6("2001:0db8:85a3::8a2e:0370:7334") is True
        assert parser._is_valid_ipv6("::1") is True
        assert parser._is_valid_ipv6("fe80::1") is True

    def test_is_valid_ipv6_invalid(self, parser):
        """Test: Rechazo de IPv6 inválido."""
        assert parser._is_valid_ipv6("192.168.1.1") is False  # Es IPv4
        assert parser._is_valid_ipv6("invalid") is False
        assert parser._is_valid_ipv6("gggg::1") is False  # 'g' no es hex
