"""Tests para el sistema de reintentos."""

import pytest

from src.core.utils.retry_decorators import retry_advanced


def test_retry_succeeds_on_first_attempt():
    """Test que la función exitosa no reintenta."""
    call_count = 0

    @retry_advanced(max_attempts=3)
    def successful_function():
        nonlocal call_count
        call_count += 1
        return "success"

    result = successful_function()
    assert result == "success"
    assert call_count == 1


def test_retry_succeeds_after_failures():
    """Test que reintenta hasta tener éxito."""
    call_count = 0

    @retry_advanced(max_attempts=3, initial_delay=0.01)
    def eventually_successful():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ValueError("Temporary error")
        return "success"

    result = eventually_successful()
    assert result == "success"
    assert call_count == 3


def test_retry_exhausts_attempts():
    """Test que levanta excepción después de agotar intentos."""

    @retry_advanced(max_attempts=3, initial_delay=0.01)
    def always_fails():
        raise ValueError("Permanent error")

    with pytest.raises(ValueError, match="Permanent error"):
        always_fails()
