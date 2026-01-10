"""
Configuración del sistema de análisis de tráfico web.
"""

import os
from dotenv import load_dotenv
from pathlib import Path


# Cargar variables de entorno
load_dotenv()

class Config:
    """
    Clase de configuracion que centraliza todos las variables de sistemas
    """

    # Configuración de la base de datos
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", 5432))
    DB_USER = os.getenv("DB_USER", "user")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
    DB_NAME = os.getenv("DB_NAME", "database")

    # Configuracion de archivos
    LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "sample_logs.txt")

    # Configuracion de procesamiento
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", 1000))

    # Configuracion de logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    LOG_DATEFMT = os.getenv("LOG_DATEFMT", "%Y-%m-%d %H:%M:%S")
    LOG_DIR = Path('logs')

    @classmethod
    def get_db_connection_string(cls):
        """
        Genera la cadena de conexión para PostgreSQL.

        Returns:
            dict: Diccionario con parámetros de conexión
        """
        return {
            'host': cls.DB_HOST,
            'port': cls.DB_PORT,
            'database': cls.DB_NAME,
            'user': cls.DB_USER,
            'password': cls.DB_PASSWORD
        }

    @classmethod
    def validate(cls):
        """
        Valida que todas las configuraciones necesarias estén presentes.

        Raises:
            ValueError: Si falta alguna configuración crítica
        """
        if not cls.DB_PASSWORD:
            raise ValueError("DB_PASSWORD no está configurado en .env")

        if not Path(cls.LOG_FILE_PATH).exists():
            print(f"Warning: Archivo de logs {cls.LOG_FILE_PATH} no encontrado")

        # Crear directorio de logs si no existe
        cls.LOG_DIR.mkdir(exist_ok=True)

        print("Configuración validada correctamente")


if __name__ != "__main__":
    try:
        Config.validate()
    except ValueError as e:
        print(f" Error de configuración: {e}")


