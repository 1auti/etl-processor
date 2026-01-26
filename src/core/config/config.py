

"""
Sistema de configuración centralizado con soporte para múltiples ambientes.
Carga configuración desde YAML y permite override con variables de entorno.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional
import yaml
from dotenv import load_dotenv

from src.core.exceptions import (
    ConfigurationError,
    InvalidConfigError,
    MissingConfigError
)


class Config:
    """
    Clase de configuración que soporta:
    - Carga desde archivos YAML (dev/test/prod)
    - Override con variables de entorno
    - Validación de configuración requerida
    - Acceso tipo diccionario y atributo
    """

    def __init__(self, env: str = None, config_dir: Path = None):
        """
        Inicializa la configuración.

        Args:
            env: Ambiente (dev/test/prod). Si None, usa ENV var o default 'dev'
            config_dir: Directorio de configs. Si None, usa ./config
        """
        # Cargar variables de entorno desde .env
        load_dotenv()

        # Determinar ambiente
        self.env = env or os.getenv('ETL_ENV', 'dev')

        # Directorio de configuración
        if config_dir is None:

            config_dir = Path("src/config")
        elif isinstance(config_dir,str):

            config_dir = Path(config_dir)

        self.config_dir = config_dir.resolve() # Convertimos en ruta absoluta

        # Configuración cargada
        self._config: Dict[str, Any] = {}

        # Cargar configuración
        self._load_config()

        # Validar configuración requerida
        self._validate_required_fields()

    def _load_config(self):
        """Carga configuración desde archivo YAML."""
        config_file = self.config_dir / f"{self.env}.yml"

        if not config_file.exists():
            raise ConfigurationError(
                f"Config file not found: {config_file}",
                {"env": self.env, "config_dir": str(self.config_dir)}
            )

        try:
            with open(config_file, 'r') as f:
                self._config = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise ConfigurationError(
                f"Failed to parse config file: {config_file}",
                {"error": str(e)}
            )

        # Override con variables de entorno
        self._apply_env_overrides()

    def _apply_env_overrides(self):
        """
        Aplica overrides desde variables de entorno.
        Las variables con prefijo ETL_ sobrescriben la config.

        Ejemplo:
            ETL_DATABASE_HOST=localhost → config['database']['host'] = 'localhost'
        """
        for key, value in os.environ.items():
            if key.startswith('ETL_'):
                # Remover prefijo y convertir a lowercase
                config_key = key[4:].lower()

                # Separar por _ para nested keys
                keys = config_key.split('_')

                # Navegar nested dict
                current = self._config
                for k in keys[:-1]:
                    if k not in current:
                        current[k] = {}
                    current = current[k]

                # Setear valor (intentar convertir tipo)
                current[keys[-1]] = self._convert_type(value)

    def _convert_type(self, value: str) -> Any:
        """Convierte string a tipo apropiado."""
        # Boolean
        if value.lower() in ('true', 'yes', '1'):
            return True
        if value.lower() in ('false', 'no', '0'):
            return False

        # Integer
        try:
            return int(value)
        except ValueError:
            pass

        # Float
        try:
            return float(value)
        except ValueError:
            pass

        # String
        return value

    def _validate_required_fields(self):
        """Valida que todos los campos requeridos estén presentes."""
        required_fields = [
            'database.host',
            'database.port',
            'database.name',
            'database.user',
            'processing.batch_size',
            'logging.level',
        ]

        missing_fields = []

        for field in required_fields:
            try:
                self.get(field)
            except MissingConfigError:
                missing_fields.append(field)

        if missing_fields:
            raise MissingConfigError(
                "Missing required configuration fields",
                {"missing_fields": missing_fields}
            )

    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtiene valor de configuración con soporte para nested keys.

        Args:
            key: Clave de configuración (soporta dot notation: 'database.host')
            default: Valor por default si no existe

        Returns:
            Valor de configuración

        Raises:
            MissingConfigError: Si la clave no existe y no hay default

        Example:
            >>> config = Config()
            >>> config.get('database.host')
            'localhost'
            >>> config.get('database.timeout', 30)
            30
        """
        keys = key.split('.')
        value = self._config

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            if default is not None:
                return default
            raise MissingConfigError(
                f"Configuration key not found: {key}",
                {"key": key, "env": self.env}
            )

    def __getitem__(self, key: str) -> Any:
        """Permite acceso tipo diccionario: config['database']"""
        return self.get(key)

    def __getattr__(self, key: str) -> Any:
        """Permite acceso tipo atributo: config.database"""
        try:
            return self._config[key]
        except KeyError:
            raise AttributeError(f"Config has no attribute '{key}'")

    def to_dict(self) -> Dict[str, Any]:
        """Retorna toda la configuración como diccionario."""
        return self._config.copy()

    def get_database_url(self) -> str:
        """
        Construye URL de conexión a PostgreSQL.

        Returns:
            str: URL en formato postgresql://user:pass@host:port/database
        """
        db = self.get('database')
        password = db.get('password', '')

        return (
            f"postgresql://{db['user']}:{password}@"
            f"{db['host']}:{db['port']}/{db['name']}"
        )

    def get_database_params(self) -> Dict[str, Any]:
        """
        Retorna parámetros de conexión para psycopg2.

        Returns:
            dict: Parámetros de conexión
        """
        db = self.get('database')
        return {
            'host': db['host'],
            'port': db['port'],
            'database': db['name'],
            'user': db['user'],
            'password': db.get('password', ''),
        }
