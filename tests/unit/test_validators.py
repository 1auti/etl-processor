"""Tests para el sistema de validadores."""
import pytest
from src.core.validators import (
    validate_ip_address,
    validate_ipv4,
    validate_url,
    validate_http_status
)

class TestIPValidators:
    """Tests de validadores de IP."""

    def test_valid_ipv4(self):
        assert validate_ipv4('192.168.1.1') is True
        assert validate_ipv4('10.0.0.1') is True

    def test_invalid_ipv4(self):
        assert validate_ipv4('256.1.1.1') is False
        assert validate_ipv4('invalid') is False

    def test_validate_ip_accepts_both_versions(self):
        assert validate_ip_address('192.168.1.1') is True
        assert validate_ip_address('2001:0db8::1') is True

class TestURLValidators:
    """Tests de validadores de URL."""

    def test_valid_http_url(self):
        assert validate_url('http://example.com') is True
        assert validate_url('https://example.com/path') is True

    def test_invalid_url(self):
        assert validate_url('not-a-url') is False
        assert validate_url('ftp://invalid') is True

class TestHTTPValidators:
    """Tests de validadores HTTP."""

    def test_valid_status_codes(self):
        assert validate_http_status(200) is True
        assert validate_http_status(404) is True
        assert validate_http_status(500) is True

    def test_invalid_status_codes(self):
        assert validate_http_status(999) is False
        assert validate_http_status(-1) is False
