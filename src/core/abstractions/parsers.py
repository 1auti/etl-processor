"""
Clases base abstractas para parsers de logs.

Los parsers son responsables de convertir líneas de log crudas
en registros estructurados con campos definidos.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from .types import LogRecord, LogRecordBatch, ParserStats


class BaseParser(ABC):
    """
    Clase base abstracta para parsers de logs.

    Define el contrato que deben seguir todos los parsers en el sistema.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Nombre del parser para propósitos de logging e identificación.

        Returns:
            str: Nombre del parser (ej: 'apache_parser', 'nginx_parser')
        """

    @property
    @abstractmethod
    def supported_formats(self) -> List[str]:
        """
        Lista de formatos de log soportados por este parser.

        Returns:
            List[str]: Formatos soportados
            Ejemplo: ['apache_common', 'apache_combined', 'nginx']
        """

    @abstractmethod
    def parse_line(self, line: str) -> Optional[LogRecord]:
        """
        Parsea una sola línea de log en un registro estructurado.

        Args:
            line: Línea de log cruda a parsear

        Returns:
            LogRecord: Registro parseado como diccionario, o None si falla el parsing
        """

    @abstractmethod
    def validate_record(self, record: LogRecord) -> bool:
        """
        Valida un registro parseado.

        Verifica que todos los campos requeridos estén presentes
        y que los valores sean válidos.

        Args:
            record: Registro parseado a validar

        Returns:
            bool: True si el registro es válido
        """

    def parse_batch(self, lines: List[str]) -> LogRecordBatch:
        """
        Parsea múltiples líneas de log en lote.

        Args:
            lines: Lista de líneas de log crudas

        Returns:
            LogRecordBatch: Lista de registros parseados exitosamente

        Nota:
            Las líneas que fallen en el parsing o validación son omitidas
            silenciosamente. Los errores se registran en las estadísticas.
        """
        records = []

        for line in lines:
            try:
                # Intentar parsear la línea
                record = self.parse_line(line)

                # Si el parsing fue exitoso y el registro es válido
                if record and self.validate_record(record):
                    records.append(record)

            except Exception:
                # Omitir líneas con error, se registran en estadísticas
                # Esto permite que el procesamiento continúe incluso con líneas malformadas
                continue

        return records

    def parse_with_stats(self, lines: List[str]) -> tuple[LogRecordBatch, ParserStats]:
        """
        Parsea un lote de líneas y retorna tanto los registros como estadísticas.

        Args:
            lines: Lista de líneas de log crudas

        Returns:
            tuple: (registros_parseados, estadísticas)
        """
        records = []
        stats = ParserStats()
        stats.total_lines = len(lines)

        for line in lines:
            try:
                record = self.parse_line(line)

                if record:
                    if self.validate_record(record):
                        records.append(record)
                        stats.parsed_successfully += 1
                    else:
                        stats.validation_errors += 1
                else:
                    stats.parse_errors += 1

            except Exception:
                stats.parse_errors += 1
                # Opcional: registrar el error específico
                continue

        return records, stats

    def can_parse(self, sample_lines: List[str]) -> float:
        """
        Evalúa si este parser puede parsear correctamente un conjunto de muestra.

        Args:
            sample_lines: Líneas de muestra para evaluar compatibilidad

        Returns:
            float: Porcentaje de éxito (0.0 a 1.0)
        """
        if not sample_lines:
            return 0.0

        parsed_count = 0

        for line in sample_lines[:10]:  # Evaluar solo las primeras 10 líneas
            try:
                record = self.parse_line(line)
                if record and self.validate_record(record):
                    parsed_count += 1
            except Exception:
                continue

        return parsed_count / min(len(sample_lines), 10)

    def get_stats(self) -> ParserStats:
        """
        Obtiene estadísticas del parser.

        Returns:
            ParserStats: Objeto con estadísticas del parser

        Nota:
            Las implementaciones concretas deben sobrescribir este método
            para proporcionar estadísticas reales.
        """
        # Implementación base - debe ser sobrescrita por las clases concretas
        return ParserStats()

    def validate_configuration(self) -> bool:
        """
        Valida la configuración del parser.

        Returns:
            bool: True si la configuración es válida

        Raises:
            ConfigurationError: Si la configuración es inválida
        """
        # Implementación base - puede ser extendida por clases concretas
        return True
