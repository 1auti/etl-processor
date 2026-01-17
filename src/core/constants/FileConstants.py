from typing import Set


class FileConstants:
    """Constantes para manejo de archivos."""

    # Extensiones soportadas
    VALID_LOG_EXTENSIONS: Set[str] = {
        '.log',
        '.txt',
        '.logs'
    }

    # Encodings soportados
    DEFAULT_ENCODING = 'utf-8'
    ALTERNATIVE_ENCODINGS = ['latin-1', 'iso-8859-1', 'cp1252']

    # Configuración de lectura
    READ_CHUNK_SIZE = 8192       # Bytes para lectura en chunks
    MAX_FILE_SIZE = 1024 * 1024 * 1024  # 1 GB

    # Directorios
    DEFAULT_LOGS_DIR = "logs"
    DEFAULT_OUTPUT_DIR = "output"
    DEFAULT_TEMP_DIR = "temp"
