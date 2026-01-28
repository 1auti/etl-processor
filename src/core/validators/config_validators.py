"""
Validadores para configuración del sistema ETL.
Valida archivos de configuración YAML y variables de entorno.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Set


def validate_config_dict(
    config: Dict[str, Any], required_keys: Optional[List[str]] = None, strict: bool = False
) -> bool:
    """
    Valida un diccionario de configuración.

    Args:
        config: Diccionario de configuración a validar
        required_keys: Lista de claves requeridas (dot notation soportada)
        strict: Si True, no permite claves vacías/None

    Returns:
        bool: True si la configuración es válida

    Raises:
        ValueError: Si la validación falla

    Example:
        >>> config = {'database': {'host': 'localhost', 'port': 5432}}
        >>> validate_config_dict(config, required_keys=['database.host', 'database.port'])
        True
    """
    if not isinstance(config, dict):
        raise ValueError(f"Config debe ser un diccionario, recibido: {type(config)}")

    if not config:
        raise ValueError("Config no puede estar vacío")

    # Validar claves requeridas
    if required_keys:
        for key in required_keys:
            if not _has_nested_key(config, key):
                raise ValueError(f"Clave requerida faltante: '{key}'")

            if strict:
                value = _get_nested_value(config, key)
                if value is None or value == "":
                    raise ValueError(f"Clave '{key}' no puede estar vacía")

    return True


def validate_database_config(config: Dict[str, Any]) -> bool:
    """
    Valida configuración específica de base de datos.

    Args:
        config: Diccionario con configuración de BD

    Returns:
        bool: True si la configuración es válida

    Raises:
        ValueError: Si la configuración es inválida

    Example:
        >>> db_config = {
        ...     'host': 'localhost',
        ...     'port': 5432,
        ...     'name': 'etl_db',
        ...     'user': 'postgres'
        ... }
        >>> validate_database_config(db_config)
        True
    """
    required_keys = ["host", "port", "name", "user"]

    for key in required_keys:
        if key not in config:
            raise ValueError(f"Configuración de BD faltante: '{key}'")

        if not config[key]:
            raise ValueError(f"Configuración de BD '{key}' no puede estar vacía")

    # Validar tipos específicos
    if not isinstance(config["port"], int):
        raise ValueError(f"Puerto debe ser entero, recibido: {type(config['port'])}")

    if not (1 <= config["port"] <= 65535):
        raise ValueError(f"Puerto inválido: {config['port']} (debe estar entre 1-65535)")

    # Validar campos opcionales si existen
    if "pool_size" in config:
        if not isinstance(config["pool_size"], int) or config["pool_size"] < 1:
            raise ValueError(f"pool_size inválido: {config.get('pool_size')}")

    if "timeout" in config:
        if not isinstance(config["timeout"], (int, float)) or config["timeout"] <= 0:
            raise ValueError(f"timeout inválido: {config.get('timeout')}")

    return True


def validate_processing_config(config: Dict[str, Any]) -> bool:
    """
    Valida configuración de procesamiento ETL.

    Args:
        config: Diccionario con configuración de procesamiento

    Returns:
        bool: True si la configuración es válida

    Raises:
        ValueError: Si la configuración es inválida

    Example:
        >>> proc_config = {
        ...     'batch_size': 1000,
        ...     'max_workers': 4,
        ...     'chunk_size': 10000
        ... }
        >>> validate_processing_config(proc_config)
        True
    """
    # Validar batch_size
    if "batch_size" in config:
        batch_size = config["batch_size"]
        if not isinstance(batch_size, int) or batch_size < 1:
            raise ValueError(f"batch_size debe ser entero positivo: {batch_size}")

        if batch_size > 100000:
            raise ValueError(f"batch_size muy grande: {batch_size} (máximo recomendado: 100000)")

    # Validar max_workers
    if "max_workers" in config:
        max_workers = config["max_workers"]
        if not isinstance(max_workers, int) or max_workers < 1:
            raise ValueError(f"max_workers debe ser entero positivo: {max_workers}")

        if max_workers > 32:
            raise ValueError(f"max_workers muy grande: {max_workers} (máximo recomendado: 32)")

    # Validar chunk_size
    if "chunk_size" in config:
        chunk_size = config["chunk_size"]
        if not isinstance(chunk_size, int) or chunk_size < 1:
            raise ValueError(f"chunk_size debe ser entero positivo: {chunk_size}")

    # Validar retry_attempts
    if "retry_attempts" in config:
        retry = config["retry_attempts"]
        if not isinstance(retry, int) or retry < 0:
            raise ValueError(f"retry_attempts debe ser entero no negativo: {retry}")

        if retry > 10:
            raise ValueError(f"retry_attempts muy grande: {retry} (máximo recomendado: 10)")

    return True


def validate_logging_config(config: Dict[str, Any]) -> bool:
    """
    Valida configuración de logging.

    Args:
        config: Diccionario con configuración de logging

    Returns:
        bool: True si la configuración es válida

    Raises:
        ValueError: Si la configuración es inválida
    """
    valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}

    if "level" in config:
        level = config["level"].upper() if isinstance(config["level"], str) else config["level"]
        if level not in valid_levels:
            raise ValueError(
                f"Nivel de logging inválido: '{config['level']}'. "
                f"Valores válidos: {valid_levels}"
            )

    if "log_file" in config:
        log_file = Path(config["log_file"])
        # Validar que el directorio padre existe o se puede crear
        if not log_file.parent.exists():
            try:
                log_file.parent.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                raise ValueError(f"No se puede crear directorio de logs: {e}")

    if "max_file_size_mb" in config:
        size = config["max_file_size_mb"]
        if not isinstance(size, (int, float)) or size <= 0:
            raise ValueError(f"max_file_size_mb inválido: {size}")

    if "backup_count" in config:
        count = config["backup_count"]
        if not isinstance(count, int) or count < 0:
            raise ValueError(f"backup_count inválido: {count}")

    return True


def validate_file_paths_config(config: Dict[str, Any]) -> bool:
    """
    Valida configuración de rutas de archivos.

    Args:
        config: Diccionario con configuración de paths

    Returns:
        bool: True si la configuración es válida

    Raises:
        ValueError: Si la configuración es inválida
    """
    path_keys = ["input_dir", "output_dir", "processed_dir", "failed_dir", "checkpoint_dir"]

    for key in path_keys:
        if key in config:
            path_str = config[key]

            if not isinstance(path_str, str):
                raise ValueError(f"{key} debe ser string, recibido: {type(path_str)}")

            if not path_str.strip():
                raise ValueError(f"{key} no puede estar vacío")

            path = Path(path_str)

            # Validar que no sea ruta absoluta peligrosa
            if path.is_absolute():
                # Permitir rutas absolutas pero advertir sobre rutas de sistema
                dangerous_paths = ["/bin", "/usr", "/etc", "/sys", "/proc"]
                if any(str(path).startswith(dp) for dp in dangerous_paths):
                    raise ValueError(f"{key} apunta a directorio de sistema: {path}")

    return True


def validate_env_vars(
    env_vars: Dict[str, str], required_vars: Optional[Set[str]] = None, prefix: Optional[str] = None
) -> bool:
    """
    Valida variables de entorno.

    Args:
        env_vars: Diccionario de variables de entorno
        required_vars: Set de variables requeridas
        prefix: Prefijo esperado para las variables (ej: 'ETL_')

    Returns:
        bool: True si las variables son válidas

    Raises:
        ValueError: Si la validación falla

    Example:
        >>> env_vars = {'ETL_DATABASE_HOST': 'localhost', 'ETL_DATABASE_PORT': '5432'}
        >>> validate_env_vars(env_vars, required_vars={'ETL_DATABASE_HOST'}, prefix='ETL_')
        True
    """
    if not isinstance(env_vars, dict):
        raise ValueError(f"env_vars debe ser diccionario, recibido: {type(env_vars)}")

    # Validar variables requeridas
    if required_vars:
        missing_vars = required_vars - set(env_vars.keys())
        if missing_vars:
            raise ValueError(f"Variables de entorno faltantes: {missing_vars}")

    # Validar prefijo
    if prefix:
        for key in env_vars.keys():
            if not key.startswith(prefix):
                raise ValueError(f"Variable '{key}' no tiene el prefijo esperado '{prefix}'")

    # Validar que no haya valores vacíos en variables requeridas
    if required_vars:
        for var in required_vars:
            if var in env_vars and not env_vars[var]:
                raise ValueError(f"Variable de entorno '{var}' no puede estar vacía")

    return True


def validate_metrics_config(config: Dict[str, Any]) -> bool:
    """
    Valida configuración de métricas.

    Args:
        config: Diccionario con configuración de métricas

    Returns:
        bool: True si la configuración es válida

    Raises:
        ValueError: Si la configuración es inválida
    """
    if "collection_interval_seconds" in config:
        interval = config["collection_interval_seconds"]
        if not isinstance(interval, (int, float)) or interval <= 0:
            raise ValueError(f"collection_interval_seconds inválido: {interval}")

        if interval < 1:
            raise ValueError(
                f"collection_interval_seconds muy pequeño: {interval} "
                "(mínimo recomendado: 1 segundo)"
            )

    if "enable_prometheus" in config:
        if not isinstance(config["enable_prometheus"], bool):
            raise ValueError(f"enable_prometheus debe ser booleano: {config['enable_prometheus']}")

    if "prometheus_port" in config:
        port = config["prometheus_port"]
        if not isinstance(port, int) or not (1024 <= port <= 65535):
            raise ValueError(f"prometheus_port inválido: {port} (debe estar entre 1024-65535)")

    return True


def validate_full_config(config: Dict[str, Any]) -> Dict[str, bool]:
    """
    Valida configuración completa del sistema ETL.

    Args:
        config: Configuración completa a validar

    Returns:
        Dict[str, bool]: Diccionario con resultado de cada sección

    Example:
        >>> config = {
        ...     'database': {'host': 'localhost', 'port': 5432, 'name': 'db', 'user': 'user'},
        ...     'processing': {'batch_size': 1000},
        ...     'logging': {'level': 'INFO'}
        ... }
        >>> results = validate_full_config(config)
        >>> all(results.values())
        True
    """
    results = {}

    # Validar sección database
    if "database" in config:
        try:
            results["database"] = validate_database_config(config["database"])
        except ValueError as e:
            results["database"] = False
            results["database_error"] = str(e)

    # Validar sección processing
    if "processing" in config:
        try:
            results["processing"] = validate_processing_config(config["processing"])
        except ValueError as e:
            results["processing"] = False
            results["processing_error"] = str(e)

    # Validar sección logging
    if "logging" in config:
        try:
            results["logging"] = validate_logging_config(config["logging"])
        except ValueError as e:
            results["logging"] = False
            results["logging_error"] = str(e)

    # Validar sección files
    if "files" in config:
        try:
            results["files"] = validate_file_paths_config(config["files"])
        except ValueError as e:
            results["files"] = False
            results["files_error"] = str(e)

    # Validar sección metrics
    if "metrics" in config:
        try:
            results["metrics"] = validate_metrics_config(config["metrics"])
        except ValueError as e:
            results["metrics"] = False
            results["metrics_error"] = str(e)

    return results


# ========== FUNCIONES AUXILIARES PRIVADAS ==========


def _has_nested_key(data: Dict[str, Any], key_path: str) -> bool:
    """
    Verifica si existe una clave anidada usando dot notation.

    Args:
        data: Diccionario a buscar
        key_path: Ruta de la clave con dot notation (ej: 'database.host')

    Returns:
        bool: True si la clave existe
    """
    keys = key_path.split(".")
    current = data

    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return False
        current = current[key]

    return True


def _get_nested_value(data: Dict[str, Any], key_path: str) -> Any:
    """
    Obtiene valor de clave anidada usando dot notation.

    Args:
        data: Diccionario a buscar
        key_path: Ruta de la clave con dot notation

    Returns:
        Any: Valor encontrado o None
    """
    keys = key_path.split(".")
    current = data

    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]

    return current
