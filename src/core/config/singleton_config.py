
from typing import Optional
from config import Config


_config_instance: Optional[Config] = None


def get_config(env: str = None, reload: bool = False) -> Config:
    """
    Obtiene instancia singleton de Config.

    Args:
        env: Ambiente a cargar (dev/test/prod)
        reload: Si True, recarga la configuración

    Returns:
        Config: Instancia de configuración

    Example:
        >>> config = get_config()
        >>> db_host = config.get('database.host')
    """
    global _config_instance

    if _config_instance is None or reload:
        _config_instance = Config(env=env)

    return _config_instance
