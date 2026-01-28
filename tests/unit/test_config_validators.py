"""
Tests para validadores de configuración.
"""

import pytest

from src.core.validators import (
    validate_config_dict,
    validate_database_config,
    validate_env_vars,
    validate_processing_config,
)


class TestConfigDictValidator:
    """Tests para validate_config_dict."""

    def test_valid_config(self):
        """Test configuración válida."""
        config = {"key": "value", "nested": {"inner": "data"}}
        assert validate_config_dict(config) is True

    def test_empty_config_raises_error(self):
        """Test que config vacío levanta error."""
        with pytest.raises(ValueError, match="vacío"):
            validate_config_dict({})

    def test_required_keys_validation(self):
        """Test validación de claves requeridas."""
        config = {"database": {"host": "localhost", "port": 5432}}
        assert (
            validate_config_dict(config, required_keys=["database.host", "database.port"]) is True
        )

    def test_missing_required_key_raises_error(self):
        """Test que clave requerida faltante levanta error."""
        config = {"database": {"host": "localhost"}}
        with pytest.raises(ValueError, match="faltante"):
            validate_config_dict(config, required_keys=["database.port"])


class TestDatabaseConfigValidator:
    """Tests para validate_database_config."""

    def test_valid_database_config(self):
        """Test config de BD válida."""
        config = {"host": "localhost", "port": 5432, "name": "etl_db", "user": "postgres"}
        assert validate_database_config(config) is True

    def test_missing_required_field_raises_error(self):
        """Test que campo requerido faltante levanta error."""
        config = {"host": "localhost", "port": 5432}
        with pytest.raises(ValueError, match="faltante"):
            validate_database_config(config)

    def test_invalid_port_raises_error(self):
        """Test que puerto inválido levanta error."""
        config = {"host": "localhost", "port": 99999, "name": "db", "user": "user"}
        with pytest.raises(ValueError, match="Puerto inválido"):
            validate_database_config(config)


class TestProcessingConfigValidator:
    """Tests para validate_processing_config."""

    def test_valid_processing_config(self):
        """Test config de procesamiento válida."""
        config = {"batch_size": 1000, "max_workers": 4, "chunk_size": 10000}
        assert validate_processing_config(config) is True

    def test_negative_batch_size_raises_error(self):
        """Test que batch_size negativo levanta error."""
        config = {"batch_size": -1}
        with pytest.raises(ValueError, match="batch_size"):
            validate_processing_config(config)


class TestEnvVarsValidator:
    """Tests para validate_env_vars."""

    def test_valid_env_vars(self):
        """Test variables de entorno válidas."""
        env_vars = {"ETL_DATABASE_HOST": "localhost", "ETL_DATABASE_PORT": "5432"}
        assert (
            validate_env_vars(env_vars, required_vars={"ETL_DATABASE_HOST"}, prefix="ETL_") is True
        )

    def test_missing_required_var_raises_error(self):
        """Test que variable requerida faltante levanta error."""
        env_vars = {"ETL_DATABASE_HOST": "localhost"}
        with pytest.raises(ValueError, match="faltantes"):
            validate_env_vars(env_vars, required_vars={"ETL_DATABASE_HOST", "ETL_DATABASE_PORT"})
