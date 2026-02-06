"""
Streaming parser para procesamiento en tiempo real de logs.

Permite procesar archivos masivos (GB/TB) sin cargar todo en memoria.
Implementa backpressure y procesamiento asíncrono opcional.

Uso:
    >>> from src.parsers import StreamingParser, ApacheParser
    >>>
    >>> parser = ApacheParser()
    >>> streamer = StreamingParser(parser)
    >>>
    >>> for record in streamer.stream_file('huge_log.log'):
    ...     process_record(record)
"""

import time
from pathlib import Path
from typing import Callable, Iterator, Optional

from src.core.abstractions.parsers import BaseParser
from src.core.abstractions.types import LogRecord
from src.core.logger import get_logger

logger = get_logger(__name__)


class StreamingParser:
    """
    Parser optimizado para streaming de archivos grandes.

    Características:
    - Memory-efficient (solo 1 línea en memoria)
    - Progress tracking
    - Rate limiting opcional
    - Callbacks para procesamiento custom

    Ejemplo:
        >>> def my_callback(record):
        ...     print(f"Procesando: {record['ip']}")
        >>>
        >>> parser = StreamingParser(ApacheParser(), callback=my_callback)
        >>> stats = parser.stream_file('access.log')
    """

    def __init__(
        self,
        parser: BaseParser,
        callback: Optional[Callable[[LogRecord], None]] = None,
        buffer_size: int = 8192,
        progress_interval: int = 10000,
    ):
        """
        Inicializa el streaming parser.

        Args:
            parser: Parser a usar (ApacheParser, NginxParser)
            callback: Función a llamar por cada registro parseado
            buffer_size: Tamaño del buffer de lectura (bytes)
            progress_interval: Cada cuántas líneas loggear progreso
        """
        self.parser = parser
        self.callback = callback
        self.buffer_size = buffer_size
        self.progress_interval = progress_interval

        # Estadísticas
        self._stats = {
            "total_lines": 0,
            "parsed_successfully": 0,
            "parse_errors": 0,
            "bytes_processed": 0,
            "start_time": None,
            "end_time": None,
        }

    def stream_file(
        self,
        file_path: str,
        encoding: str = "utf-8",
        skip_invalid: bool = True,
        rate_limit: Optional[int] = None,
    ) -> Iterator[LogRecord]:
        """
        Procesa un archivo en modo streaming.

        Args:
            file_path: Ruta al archivo
            encoding: Encoding del archivo
            skip_invalid: Si True, omite líneas inválidas
            rate_limit: Máximo de registros por segundo (None = sin límite)

        Yields:
            LogRecord: Registros parseados uno a uno

        Ejemplo:
            >>> streamer = StreamingParser(ApacheParser())
            >>> for record in streamer.stream_file('access.log'):
            ...     db.insert(record)
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")

        logger.info(
            "Iniciando streaming parsing",
            extra={"file": str(file_path), "parser": self.parser.name, "rate_limit": rate_limit},
        )

        self._stats["start_time"] = time.time()
        last_progress_log = 0
        last_rate_limit_check = time.time()
        records_this_second = 0

        try:
            with open(file_path, "r", encoding=encoding, buffering=self.buffer_size) as f:
                for line_number, line in enumerate(f, start=1):
                    self._stats["total_lines"] += 1
                    self._stats["bytes_processed"] += len(line.encode(encoding))

                    # Progress logging
                    if self._stats["total_lines"] - last_progress_log >= self.progress_interval:
                        self._log_progress()
                        last_progress_log = self._stats["total_lines"]

                    # Rate limiting
                    if rate_limit:
                        current_time = time.time()

                        # Reset contador cada segundo
                        if current_time - last_rate_limit_check >= 1.0:
                            records_this_second = 0
                            last_rate_limit_check = current_time

                        # Si excedimos el límite, esperar
                        if records_this_second >= rate_limit:
                            sleep_time = 1.0 - (current_time - last_rate_limit_check)
                            if sleep_time > 0:
                                time.sleep(sleep_time)
                            records_this_second = 0
                            last_rate_limit_check = time.time()

                    # Saltar líneas vacías/comentarios
                    stripped = line.strip()
                    if not stripped or stripped.startswith("#"):
                        continue

                    # Parsear
                    try:
                        record = self.parser.parse_line(line)

                        if record is None:
                            self._stats["parse_errors"] += 1
                            if not skip_invalid:
                                raise ValueError(f"Parse failed en línea {line_number}")
                            continue

                        # Validar
                        if not self.parser.validate_record(record):
                            self._stats["parse_errors"] += 1
                            if not skip_invalid:
                                raise ValueError(f"Validation failed en línea {line_number}")
                            continue

                        # Éxito
                        self._stats["parsed_successfully"] += 1
                        records_this_second += 1

                        # Agregar metadata
                        record["_line_number"] = line_number
                        record["_source_file"] = str(file_path)

                        # Callback (si existe)
                        if self.callback:
                            self.callback(record)

                        yield record

                    except Exception as e:
                        self._stats["parse_errors"] += 1

                        if not skip_invalid:
                            raise

                        logger.debug(f"Error en línea {line_number}: {str(e)}")

        finally:
            self._stats["end_time"] = time.time()
            self._log_final_stats()

    def _log_progress(self):
        """Loggea progreso actual."""
        elapsed = time.time() - self._stats["start_time"]
        rate = self._stats["total_lines"] / elapsed if elapsed > 0 else 0

        logger.info(
            f"Progreso: {self._stats['total_lines']} líneas procesadas",
            extra={
                "parsed": self._stats["parsed_successfully"],
                "errors": self._stats["parse_errors"],
                "rate_lines_per_sec": round(rate, 2),
            },
        )

    def _log_final_stats(self):
        """Loggea estadísticas finales."""
        elapsed = self._stats["end_time"] - self._stats["start_time"]

        logger.info(
            "Streaming parsing completado",
            extra={
                "total_lines": self._stats["total_lines"],
                "parsed": self._stats["parsed_successfully"],
                "errors": self._stats["parse_errors"],
                "duration_seconds": round(elapsed, 2),
                "avg_rate_lines_per_sec": (
                    round(self._stats["total_lines"] / elapsed, 2) if elapsed > 0 else 0
                ),
                "bytes_processed_mb": round(self._stats["bytes_processed"] / 1024 / 1024, 2),
            },
        )

    def get_stats(self) -> dict:
        """Retorna estadísticas del streaming."""
        return self._stats.copy()
