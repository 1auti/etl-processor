"""Tests unitarios para el sistema de configuración."""
import pytest
from src.core.config import Config
from src.core.exceptions import ConfigurationError

def test_config_loads_dev_environment():
    """Test que carga configuración de desarrollo."""
    config = Config(env='dev')
    assert config.env == 'dev'
    assert config.get('database.host') is not None

def test_config_get_nested_key():
    """Test de acceso a claves anidadas."""
    config = Config(env='dev')
    host = config.get('database.host')
    assert isinstance(host, str)

def test_config_missing_key_returns_default():
    """Test que retorna default para clave faltante."""
    config = Config(env='dev')
    value = config.get('non.existent.key', default='default_value')
    assert value == 'default_value'

def test_config_invalid_env_raises_error():
    """Test que levanta error con ambiente inválido."""
    with pytest.raises(ConfigurationError):
        Config(env='invalid_env_xyz')
