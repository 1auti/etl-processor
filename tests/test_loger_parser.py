"""
Tests unitarios para el LogParser.
Verifica que el parseo de logs funcione correctamente.
"""

from datetime import datetime

import pytest

from src.log_parser import LogParser

# ========== FIXTURES ==========


@pytest.fixture
def parser():
    """Fixture que proporciona una instancia del parser."""
    return LogParser()


@pytest.fixture
def valid_log_line():
    """Fixture con una línea de log válida."""
    return '192.168.1.100 - - [10/Jan/2026:14:23:45 +0000] "GET /home HTTP/1.1" 200 4523'


@pytest.fixture
def invalid_log_lines():
    """Fixture con líneas de log inválidas."""
    return [
        "linea completamente invalida",
        '192.168.1.100 - - [fecha mal formada] "GET /home" 200 4523',
        "",  # línea vacía
        "   ",  # solo espacios
    ]


# ========== TESTS DE PARSEO EXITOSO ==========


class TestLogParserSuccess:
    """Tests para casos de parseo exitoso."""

    def test_parse_valid_line(self, parser, valid_log_line):
        """Verifica que una línea válida se parsee correctamente."""
        result = parser.parse_line(valid_log_line)

        assert result is not None
        assert result["ip"] == "192.168.1.100"
        assert result["method"] == "GET"
        assert result["url"] == "/home"
        assert result["status"] == 200
        assert result["bytes"] == 4523
        assert isinstance(result["timestamp"], datetime)

    def test_parse_post_request(self, parser):
        """Verifica que se parseen correctamente requests POST."""
        line = '10.0.0.5 - - [10/Jan/2026:14:26:01 +0000] "POST /login HTTP/1.1" 401 234'
        result = parser.parse_line(line)

        assert result is not None
        assert result["method"] == "POST"
        assert result["url"] == "/login"
        assert result["status"] == 401

    def test_parse_different_ips(self, parser):
        """Verifica que se parseen correctamente diferentes IPs."""
        test_cases = [
            (
                "192.168.1.1",
                '192.168.1.1 - - [10/Jan/2026:14:23:45 +0000] "GET / HTTP/1.1" 200 100',
            ),
            ("10.0.0.1", '10.0.0.1 - - [10/Jan/2026:14:23:45 +0000] "GET / HTTP/1.1" 200 100'),
            ("172.16.0.1", '172.16.0.1 - - [10/Jan/2026:14:23:45 +0000] "GET / HTTP/1.1" 200 100'),
        ]

        for expected_ip, log_line in test_cases:
            result = parser.parse_line(log_line)
            assert result["ip"] == expected_ip

    def test_parse_different_status_codes(self, parser):
        """Verifica que se parseen correctamente diferentes códigos de estado."""
        status_codes = [200, 201, 301, 404, 500]

        for status in status_codes:
            line = f'192.168.1.1 - - [10/Jan/2026:14:23:45 +0000] "GET /test HTTP/1.1" {status} 100'
            result = parser.parse_line(line)
            assert result["status"] == status

    def test_parse_large_response(self, parser):
        """Verifica que se manejen correctamente respuestas grandes."""
        line = '192.168.1.1 - - [10/Jan/2026:14:23:45 +0000] "GET /download HTTP/1.1" 200 999999999'
        result = parser.parse_line(line)

        assert result is not None
        assert result["bytes"] == 999999999

    def test_parse_complex_url(self, parser):
        """Verifica que se parseen URLs complejas con paths y query strings."""
        line = '192.168.1.1 - - [10/Jan/2026:14:23:45 +0000] "GET /api/users?id=123&sort=asc HTTP/1.1" 200 500'
        result = parser.parse_line(line)

        assert result is not None
        assert "/api/users?id=123&sort=asc" in result["url"]


# ========== TESTS DE PARSEO FALLIDO ==========


class TestLogParserFailure:
    """Tests para casos de parseo fallido."""

    def test_parse_invalid_lines(self, parser, invalid_log_lines):
        """Verifica que líneas inválidas retornen None."""
        for line in invalid_log_lines:
            result = parser.parse_line(line)
            assert result is None

    def test_parse_empty_string(self, parser):
        """Verifica que string vacío retorne None."""
        result = parser.parse_line("")
        assert result is None

    def test_parse_malformed_timestamp(self, parser):
        """Verifica que timestamps mal formados retornen None."""
        line = '192.168.1.1 - - [INVALID_DATE] "GET /home HTTP/1.1" 200 100'
        result = parser.parse_line(line)
        assert result is None


# ========== TESTS DE VALIDACIÓN ==========


class TestValidationMethods:
    """Tests para métodos de validación."""

    def test_validate_ip_valid(self, parser):
        """Verifica que IPs válidas pasen la validación."""
        valid_ips = ["192.168.1.1", "10.0.0.1", "172.16.0.1", "8.8.8.8"]

        for ip in valid_ips:
            assert parser.validate_ip(ip) is True

    def test_validate_ip_invalid(self, parser):
        """Verifica que IPs inválidas no pasen la validación."""
        invalid_ips = [
            "256.1.1.1",  # octeto > 255
            "192.168.1",  # faltan octetos
            "192.168.1.1.1",  # demasiados octetos
            "not.an.ip.address",
            "",
        ]

        for ip in invalid_ips:
            assert parser.validate_ip(ip) is False

    def test_is_error_status(self, parser):
        """Verifica la detección de códigos de error."""
        # Códigos de éxito (2xx y 3xx)
        assert parser.is_error_status(200) is False
        assert parser.is_error_status(301) is False

        # Códigos de error (4xx y 5xx)
        assert parser.is_error_status(404) is True
        assert parser.is_error_status(500) is True


# ========== TESTS PARAMETRIZADOS ==========


@pytest.mark.parametrize(
    "method,expected",
    [
        ("GET", "GET"),
        ("POST", "POST"),
        ("PUT", "PUT"),
        ("DELETE", "DELETE"),
        ("PATCH", "PATCH"),
    ],
)
def test_parse_http_methods(parser, method, expected):
    """Verifica que se parseen correctamente todos los métodos HTTP."""
    line = f'192.168.1.1 - - [10/Jan/2026:14:23:45 +0000] "{method} /test HTTP/1.1" 200 100'
    result = parser.parse_line(line)

    assert result is not None
    assert result["method"] == expected


@pytest.mark.parametrize(
    "ip,is_valid",
    [
        ("192.168.1.1", True),
        ("10.0.0.1", True),
        ("256.1.1.1", False),
        ("192.168.1", False),
        ("invalid", False),
    ],
)
def test_ip_validation_parametrized(parser, ip, is_valid):
    """Test parametrizado para validación de IPs."""
    assert parser.validate_ip(ip) == is_valid


# ========== TESTS DE PERFORMANCE ==========


class TestPerformance:
    """Tests de rendimiento del parser."""

    def test_parse_batch_performance(self, parser, valid_log_line):
        """Verifica que el parseo en lote sea eficiente."""
        import time

        # Crear 10,000 líneas de log
        lines = [valid_log_line] * 10_000

        start_time = time.time()
        results = [parser.parse_line(line) for line in lines]
        end_time = time.time()

        duration = end_time - start_time

        # Verificar que se parsearon todas las líneas
        assert len(results) == 10_000
        assert all(r is not None for r in results)

        # Debería parsear 10k líneas en menos de 5 segundos
        assert duration < 5.0

        print(f"\n⏱️  Parseadas 10,000 líneas en {duration:.2f}s")
        print(f"   ({10_000/duration:.0f} líneas/segundo)")


# ========== TESTS DE INTEGRACIÓN ==========


class TestIntegration:
    """Tests de integración del parser."""

    def test_parse_sample_logs_file(self, parser):
        """Verifica que se pueda parsear el archivo de logs de ejemplo."""
        from pathlib import Path

        log_file = Path("sample_logs.txt")

        if not log_file.exists():
            pytest.skip("sample_logs.txt no encontrado")

        with open(log_file, "r") as f:
            lines = f.readlines()

        results = [parser.parse_line(line.strip()) for line in lines]
        successful = [r for r in results if r is not None]

        # Verificar que se parseó al menos el 80% de las líneas
        success_rate = len(successful) / len(lines)
        assert success_rate >= 0.8

        print(f"\n✅ Parseadas {len(successful)}/{len(lines)} líneas ({success_rate*100:.1f}%)")


# ========== EJECUTAR TESTS ==========

if __name__ == "__main__":
    # Ejecutar tests con pytest
    pytest.main([__file__, "-v", "--tb=short"])
