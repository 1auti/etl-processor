"""
Módulo de parsers para diferentes formatos de logs de servidores web.

Este módulo proporciona:
- Parsers especializados (Apache, Nginx)
- Factory para crear parsers automáticamente
- Abstracción base para implementar nuevos parsers

Uso básico:
    >>> from src.parsers import ParserFactory
    >>>
    >>> # Autodetección de formato
    >>> sample_lines = read_first_lines('access.log')
    >>> parser = ParserFactory.detect_and_create(sample_lines)
    >>>
    >>> # Parseo de líneas
    >>> for line in read_log_file('access.log'):
    ...     record = parser.parse_line(line)
    ...     if record:
    ...         process_record(record)

Parsers disponibles:
- ApacheParser: Apache Common y Combined Log Format
- NginxParser: Nginx Combined Log Format (con campos opcionales)

Para agregar un nuevo parser:
1. Heredar de BaseParser
2. Implementar métodos abstractos (parse_line, validate_record)
3. Agregar a ParserFactory._available_parsers
"""

from src.parsers.apache_parser import ApacheParser
from src.parsers.file_parser import FileParser
from src.parsers.nginx_parser import NginxParser
from src.parsers.parser_factory import ParserFactory
from src.parsers.streaming_parser import StreamingParser

# Exportar clases públicas
__all__ = ["ApacheParser", "NginxParser", "ParserFactory", "FileParser", "StreamingParser"]

# Metadata del módulo
__version__ = "1.0.0"
__author__ = "Lautaro Julian"


# Función helper para obtener parser por nombre (opcional)
def get_parser(parser_type: str):
    """
    Obtiene una instancia de parser por su tipo.

    Args:
        parser_type: Tipo de parser ('apache' o 'nginx')

    Returns:
        Instancia del parser solicitado

    Raises:
        ValueError: Si el tipo de parser no existe

    Ejemplo:
        >>> parser = get_parser('nginx')
        >>> print(parser.name)
        'nginx_parser'
    """
    return ParserFactory.create_parser(parser_type)
