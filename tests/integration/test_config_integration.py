import json

from src.core.config.singleton_config import get_config


def test_config_example_usage():
    """Test que replica el ejemplo pero con verificaciones"""
    config = get_config(env="dev")

    # 1. Acceso a configuración (con verificaciones)
    db_host = config.get("database.host")
    batch_size = config.get("processing.batch_size")
    log_level = config.get("logging.level")

    assert db_host is not None
    assert isinstance(batch_size, int)
    assert batch_size > 0
    assert log_level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    # 2. URL de base de datos
    db_url = config.get_database_url()
    assert db_url is not None
    assert isinstance(db_url, str)
    # Verificar formato básico de URL
    assert "://" in db_url
    if "postgresql" in db_url:
        assert db_host in db_url

    # 3. Configuración completa serializable
    config_dict = config.to_dict()
    assert isinstance(config_dict, dict)

    # Debe poder serializarse a JSON
    json_str = json.dumps(config_dict)
    parsed_back = json.loads(json_str)
    assert parsed_back == config_dict

    # 4. Verificar que todos los paths necesarios existen
    required_paths = ["database.host", "database.port", "processing.batch_size", "logging.level"]

    for path in required_paths:
        assert config.get(path) is not None, f"Missing config path: {path}"
