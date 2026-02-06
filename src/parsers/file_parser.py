import os
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, List, Optional

from src.core.abstractions.parsers import BaseParser
from src.core.abstractions.types import LogRecord
from src.core.exceptions import FileError, FileNotFoundExcepction, ParsingError
from src.core.exceptions.file.file_corrupted_error import FileCorruptedError
from src.core.logger import get_logger

logger = get_logger(__name__)


class FileParser:
    """Context manager para parser archivo de log
    Caracteristicas:
    - Manejo automatico de apertura / cierre de archivos
    - Encoding configurable
    - Tracking de lineas procesados
    - Manejo robusto de errores
    """

    def __init__(
        self, file_path: str, parser: BaseParser, encoding: str = "utf-8", skip_invalid=True
    ):
        """Inicializacion parser de archivos

        Args:
        - file_path: Ruta al archivo de log
        - parser: Instancia de parser (ApacheParser, NginxParser, etc)
        - encoding: Encoding del archivo (default -> utf-8)
        -skip_invalid: Si True, omite lineas invalidas; si False, lanza excepcion

        Raises:
         FileNotFoundException : Si el archivo no existe
        """

        self.file_path = Path(file_path)
        self.parser = parser
        self.encoding = encoding
        self.skip_invalid = skip_invalid

        # File handler (se ejecuta en enter)
        self._file_handler = None

        # Estadisticas
        self._stats = {
            "total_lines": 0,
            "parsed_successfully": 0,
            "parse_errors": 0,
            "validation_errors": 0,
            "bytes_read": 0,
        }

        # Validar que el archivo existe
        if not self.file_path.exists():
            raise FileNotFoundExcepction(f"Archivo no encontrado: {file_path}")

        # Validamos que sea un archivo
        if not self.file_path.is_file():
            raise ValueError(f"La ruta es un archivo: {file_path}")

        # Validamos que el archivo no este corrupto
        self._validate_file_integrity()

        logger.info(
            "FileParser init",
            extra={
                "file": str(self.file_path),
                "parser": self.parser.name,
                "encoding": self.encoding,
                "file_size_mb": self.file_path.stat().st_size / 1024 / 1024,
            },
        )

    def __enter__(self):
        """
        Abre el archivo al entrar al contexto

        Returns:
           self para permitir acceso a metodos
        """

        try:
            self._file_handler = open(
                self.file_path,
                "r",
                encoding=self.encoding,
                errors="replace",  # Remplaza caracteres invalidos en vez de fallar
            )
            logger.debug(f"Archivo abierto: {self.file_path}")
            return self

        except UnicodeDecodeError as e:
            logger.error(f"Error de encoding al abrir archivo: {e}")
            raise ParsingError("Error de encoding. Intenta con encoding='latin-1' o 'cp1252'")

        except Exception as e:
            logger.error(f"Error al abrir archivo: {e}")
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cierra el archivo al salir del contexto

        Args:
        exc_type -> Tipo de excepcion ( si ocurre )
        exc_val -> Valor de la excepcion
        exc_tb -> Traceback de la excepcion

        Returns:
         False para propagar excepcion"""

        if self._file_handle:
            self._file_handle.close()
            logger.debug(f"Archivo cerrado: {self.file_path}")

        # Log de estadísticas finales
        logger.info("Parsing completado", extra={"file": str(self.file_path), "stats": self._stats})

        # No suprimir excepciones
        return False

    def parse(self, batch_size: Optional[int] = None) -> Iterator[LogRecord]:
        """
        Generator que parsea el archivo línea por línea.

        Este es el método PRINCIPAL para streaming parsing.
        Usa yield para retornar registros uno a uno sin cargar
        todo el archivo en memoria.

        Args:
            batch_size: Si se especifica, procesa en batches (None = línea por línea)

        Yields:
            LogRecord: Registro parseado y validado

        Raises:
            ParsingError: Si skip_invalid=False y encuentra línea inválida

        Ejemplo:
            >>> with FileParser('access.log', ApacheParser()) as fp:
            ...     for record in fp.parse():
            ...         print(f"IP: {record['ip']}, Status: {record['status']}")

        NOTA: Este método debe llamarse DENTRO del context manager.
        """
        if not self._file_handle:
            raise RuntimeError("FileParser debe usarse dentro de 'with' statement")

        logger.info(f"Iniciando streaming parsing de {self.file_path}")

        for line_number, line in enumerate(self._file_handle, start=1):
            # Actualizar estadísticas
            self._stats["total_lines"] += 1
            self._stats["bytes_read"] += len(line.encode(self.encoding))

            # Saltar líneas vacías o comentarios
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            # Intentar parsear
            try:
                record = self.parser.parse_line(line)

                if record is None:
                    self._stats["parse_errors"] += 1

                    if not self.skip_invalid:
                        raise ParsingError(f"Error parseando línea {line_number}: {line[:100]}")

                    logger.debug(f"Línea {line_number} omitida (parse failed)")
                    continue

                # Validar el registro
                if not self.parser.validate_record(record):
                    self._stats["validation_errors"] += 1

                    if not self.skip_invalid:
                        raise ParsingError(f"Registro inválido en línea {line_number}")

                    logger.debug(f"Línea {line_number} omitida (validation failed)")
                    continue

                # Registro válido - actualizar stats y yield
                self._stats["parsed_successfully"] += 1

                # Agregar metadata adicional
                record["_line_number"] = line_number
                record["_source_file"] = str(self.file_path)

                yield record

            except Exception as e:
                self._stats["parse_errors"] += 1

                if not self.skip_invalid:
                    raise ParsingError(f"Error en línea {line_number}: {str(e)}")

                logger.warning(
                    f"Error parseando línea {line_number}: {str(e)}", extra={"line": line[:100]}
                )

    def parse_batch(self, batch_size: int = 1000) -> Iterator[List[LogRecord]]:
        """
        Generator que parsea el archivo en batches.

        Útil para procesamiento por lotes (ej: bulk insert en BD).

        Args:
            batch_size: Número de registros por batch

        Yields:
            List[LogRecord]: Lista de registros parseados (máximo batch_size)

        Ejemplo:
            >>> with FileParser('access.log', ApacheParser()) as fp:
            ...     for batch in fp.parse_batch(batch_size=500):
            ...         db.bulk_insert(batch)
            ...         print(f"Insertados {len(batch)} registros")
        """
        batch = []

        for record in self.parse():
            batch.append(record)

            if len(batch) >= batch_size:
                yield batch
                batch = []

        # Yield del último batch (puede ser < batch_size)
        if batch:
            yield batch

    def get_stats(self) -> dict:
        """
        Retorna estadísticas del parsing.

        Returns:
            dict con estadísticas (total_lines, parsed_successfully, etc)

        Ejemplo:
            >>> with FileParser('access.log', parser) as fp:
            ...     list(fp.parse())  # Consumir generator
            ...     stats = fp.get_stats()
            ...     print(f"Tasa de éxito: {stats['parsed_successfully'] / stats['total_lines'] * 100}%")
        """
        return self._stats.copy()

    @property
    def success_rate(self) -> float:
        """
        Calcula la tasa de éxito del parsing.

        Returns:
            float: Porcentaje de líneas parseadas exitosamente (0-100)
        """
        total = self._stats["total_lines"]
        if total == 0:
            return 0.0

        return (self._stats["parsed_successfully"] / total) * 100

    @staticmethod
    @contextmanager
    def from_parser_type(file_path: str, parser_type: str, **kwargs):
        """
        Factory method que crea FileParser con parser por nombre.

        Args:
            file_path: Ruta al archivo
            parser_type: Tipo de parser ('apache' o 'nginx')
            **kwargs: Argumentos adicionales para FileParser

        Yields:
            FileParser configurado

        Ejemplo:
            >>> with FileParser.from_parser_type('access.log', 'apache') as fp:
            ...     for record in fp.parse():
            ...         print(record)
        """
        from src.parsers import ParserFactory

        parser = ParserFactory.create_parser(parser_type)
        if not parser:
            raise ValueError(f"Parser desconocido: {parser_type}")

        with FileParser(file_path, parser, **kwargs) as fp:
            yield fp

    def _validate_file_integrity(self) -> None:
        try:
            with self.file_path.open("rb") as f:
                chunck = f.read(1024)

                if not chunck:
                    raise FileError(f"El archivo esta vacio: {self.file_path}")

        except UnicodeDecodeError as e:
            raise FileError(
                f"Encoding invalido ({self.encoding}) para el archivo: {self.file_path}"
            ) from e

        except OSError as e:
            raise FileCorruptedError(f"El archivo esta corrupto {self.file_path}") from e
