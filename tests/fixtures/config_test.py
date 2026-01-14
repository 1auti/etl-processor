
from core.config.singleton_config import get_config
import pytest

@pytest.fixture
def dev_config():
    """Fixture: Configuración de desarrollo"""
    return get_config(env='dev')

@pytest.fixture
def prod_config():
    """Fixture: Configuración de producción"""
    return get_config(env='prod')

# tests/test_config_fixtures.py
class TestConfigWithFixtures:
    def test_dev_config_values(self, dev_config):
        """Test valores específicos de dev"""
        assert dev_config.get('database.host') == 'localhost' or '127.0.0.1'
        assert dev_config.get('logging.level') == 'DEBUG'

    def test_prod_config_security(self, prod_config):
        """Test que prod tiene configuraciones seguras"""
        assert prod_config.get('logging.level') != 'DEBUG'  # No debug en prod
        assert '@' in prod_config.get_database_url()  # Debe tener credenciales
