"""
Factory para crear parsers automáticamente según el formato detectado.

Detecta automáticamente si un log es Apache o Nginx analizando
las primeras líneas del archivo.
"""

from typing import List, Optional

from src.core.abstractions.parsers import BaseParser
from src.parsers.apache_parser import ApacheParser
from src.parsers.nginx_parser import NginxParser


class ParserFactory:
    """
    Factory que crea el parser apropiado según el formato de log.

    Uso:
        >>> factory = ParserFactory()
        >>> parser = factory.detect_and_create(['línea1', 'línea2'])
        >>> print(parser.name)
        'nginx_parser'
    """

    # Registro de parsers disponibles
    # ORDEN IMPORTA: Se prueban en este orden
    _available_parsers = [
        NginxParser,  # Probar Nginx primero (más restrictivo)
        ApacheParser,  # Apache es más flexible
    ]

    @classmethod
    def detect_and_create(
        cls,
        sample_lines: List[str],
        max_samples: int = 10,  # Aumentado de 5 a 10 para mejor detección
    ) -> Optional[BaseParser]:
        """
        Detecta automáticamente el formato y crea el parser apropiado.

        Estrategia:
        1. Toma las primeras N líneas del archivo
        2. Intenta parsear con cada parser disponible
        3. Retorna el parser que tuvo más éxitos

        Args:
            sample_lines: Primeras líneas del archivo de log
            max_samples: Cuántas líneas usar para detección (default: 10)

        Returns:
            Parser apropiado o None si no se detecta ninguno

        Ejemplo:
            >>> lines = [
            ...     '10.0.0.1 - - [29/Jan/2026:10:00:00 +0000] "GET / HTTP/1.1" 200 123 "-" "curl/7.68.0"',
            ...     '10.0.0.2 - - [29/Jan/2026:10:00:01 +0000] "POST /api HTTP/1.1" 201 456 "-" "python-requests/2.28"'
            ... ]
            >>> parser = ParserFactory.detect_and_create(lines)
            >>> print(parser.name)
            'nginx_parser'
        """
        # Limitar muestras
        samples = sample_lines[:max_samples]

        # Filtrar líneas vacías o comentarios
        samples = [line for line in samples if line.strip() and not line.startswith("#")]

        if not samples:
            return None

        # Contador de éxitos por parser
        scores = {}

        # Probar cada parser disponible
        for parser_class in cls._available_parsers:
            parser = parser_class()
            success_count = 0

            # Intentar parsear cada línea de muestra
            for line in samples:
                record = parser.parse_line(line)
                # No solo contar parseos exitosos, sino también validación
                if record and parser.validate_record(record):
                    success_count += 1

            scores[parser_class] = success_count

        # Elegir el parser con más éxitos
        if scores:
            best_parser_class = max(scores, key=scores.get)
            best_score = scores[best_parser_class]

            # Requiere al menos 50% de éxito para considerar el parser válido
            success_rate = best_score / len(samples)
            if success_rate >= 0.5:
                return best_parser_class()

        return None

    @classmethod
    def create_parser(cls, parser_type: str) -> Optional[BaseParser]:
        """
        Crea un parser específico por nombre.

        Args:
            parser_type: Tipo de parser ('apache' o 'nginx')

        Returns:
            Instancia del parser solicitado o None si no existe

        Ejemplo:
            >>> parser = ParserFactory.create_parser('nginx')
            >>> print(parser.supported_formats)
            ['nginx_combined', 'nginx_default']
        """
        parser_map = {
            "apache": ApacheParser,
            "nginx": NginxParser,
        }

        parser_class = parser_map.get(parser_type.lower())
        return parser_class() if parser_class else None

    @classmethod
    def list_available_parsers(cls) -> List[str]:
        """
        Lista todos los parsers disponibles en el sistema.

        Returns:
            Lista con nombres de parsers disponibles

        Ejemplo:
            >>> ParserFactory.list_available_parsers()
            ['nginx_parser', 'apache_parser']
        """
        return [parser().name for parser in cls._available_parsers]
