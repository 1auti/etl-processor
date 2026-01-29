"""
Clases base abstractas para extractores de datos.

Los extractores son responsables de obtener datos crudos de diferentes fuentes
(archivos locales, APIs, bases de datos, S3, FTP, etc.) y prepararlos para
el procesamiento posterior en el pipeline ETL.
"""

from abc import ABC, abstractmethod
from contextlib import AbstractContextManager
from typing import Any, Dict, Iterator, List, Optional

from .types import ExtractionResult


class BaseExtractor(AbstractContextManager):
    """
    Clase base abstracta para extractores de datos.

    Define el contrato para extraer datos de diversas fuentes.
    Hereda de AbstractContextManager para soportar el manejo automático
    de recursos (conexiones, archivos, etc.).
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Nombre del extractor para logging e identificación.

        Returns:
            str: Nombre del extractor
            Ejemplo: 'file_extractor', 's3_extractor', 'api_extractor'
        """

    @property
    @abstractmethod
    def supported_sources(self) -> List[str]:
        """
        Tipos de fuentes de datos soportadas por este extractor.

        Returns:
            List[str]: Tipos de fuentes soportadas
            Ejemplo: ['local_file', 's3', 'http_api', 'ftp', 'database']
        """

    @abstractmethod
    def extract(self) -> List[str]:
        """
        Extrae datos de la fuente configurada.

        Returns:
            List[str]: Lista de líneas/texto extraído

        Raises:
            ExtractionError: Si ocurre un error durante la extracción
            SourceNotFoundError: Si la fuente no es accesible
        """

    @abstractmethod
    def validate_source(self) -> bool:
        """
        Valida que la fuente de datos sea accesible y válida.

        Returns:
            bool: True si la fuente es válida y accesible

        Raises:
            ValidationError: Si la validación falla
        """

    @abstractmethod
    def get_source_info(self) -> Dict[str, Any]:
        """
        Obtiene información sobre la fuente de datos.

        Returns:
            Dict[str, Any]: Diccionario con información de la fuente
            Ejemplo: {'path': '/ruta/archivo.log', 'size': 1024, 'encoding': 'utf-8'}
        """

    def extract_with_metadata(self) -> ExtractionResult:
        """
        Extrae datos junto con metadatos de la extracción.

        Returns:
            ExtractionResult: Resultado con datos y metadatos
        """
        source_info = self.get_source_info()
        raw_lines = self.extract()
        errors = []

        return ExtractionResult(raw_lines=raw_lines, source_info=source_info, errors=errors)

    def get_size_estimate(self) -> Optional[int]:
        """
        Obtiene una estimación del tamaño de los datos a extraer.

        Returns:
            Optional[int]: Tamaño estimado en bytes, o None si no se puede determinar
        """
        source_info = self.get_source_info()
        return source_info.get("size")

    def health_check(self) -> Dict[str, Any]:
        """
        Realiza un chequeo de salud del extractor y la fuente.

        Returns:
            Dict[str, Any]: Estado de salud del extractor
        """
        try:
            source_valid = self.validate_source()
            source_info = self.get_source_info()

            return {
                "extractor": self.name,
                "source_valid": source_valid,
                "source_info": source_info,
                "supported_sources": self.supported_sources,
                "status": "healthy" if source_valid else "unhealthy",
            }
        except Exception as e:
            return {
                "extractor": self.name,
                "source_valid": False,
                "error": str(e),
                "status": "error",
            }


class BaseIncrementalExtractor(BaseExtractor):
    """
    Extractores incrementales con soporte para checkpointing.

    Estos extractores mantienen un estado de la última extracción
    para evitar reprocesar datos ya extraídos.
    """

    @abstractmethod
    def get_checkpoint(self) -> Optional[Dict[str, Any]]:
        """
        Obtiene el checkpoint actual de la extracción.

        Returns:
            Optional[Dict[str, Any]]: Checkpoint actual o None si es la primera ejecución
        """

    @abstractmethod
    def set_checkpoint(self, checkpoint_data: Dict[str, Any]) -> bool:
        """
        Establece un nuevo checkpoint después de una extracción exitosa.

        Args:
            checkpoint_data: Datos del checkpoint a guardar

        Returns:
            bool: True si el checkpoint se guardó exitosamente
        """

    @abstractmethod
    def extract_since_checkpoint(self, checkpoint: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        Extrae solo los datos nuevos desde el último checkpoint.

        Args:
            checkpoint: Checkpoint opcional (si None, usa el actual)

        Returns:
            List[str]: Datos nuevos desde el último checkpoint
        """


class BaseStreamingExtractor(BaseExtractor):
    """
    Extractores de streaming para fuentes de datos continuas.

    En lugar de extraer todos los datos de una vez, proporcionan
    un stream continuo de datos.
    """

    @abstractmethod
    def stream(self) -> Iterator[str]:
        """
        Genera un stream continuo de datos.

        Yields:
            str: Líneas de datos a medida que están disponibles
        """

    @abstractmethod
    def is_stream_complete(self) -> bool:
        """
        Verifica si el stream de datos ha finalizado.

        Returns:
            bool: True si el stream ha finalizado
        """

    def extract_stream_with_timeout(self, timeout_seconds: int = 30) -> List[str]:
        """
        Extrae datos del stream con un timeout.

        Args:
            timeout_seconds: Tiempo máximo de espera en segundos

        Returns:
            List[str]: Datos extraídos antes del timeout
        """
        import time
        from threading import Event, Thread

        data = []
        stop_event = Event()

        def collect_data():
            for line in self.stream():
                if stop_event.is_set():
                    break
                data.append(line)

        # Iniciar thread de colección
        collector = Thread(target=collect_data)
        collector.start()

        # Esperar timeout o fin del stream
        start_time = time.time()
        while time.time() - start_time < timeout_seconds:
            if not collector.is_alive() or self.is_stream_complete():
                break
            time.sleep(0.1)

        # Señalar parada
        stop_event.set()
        collector.join(timeout=5)

        return data


class BaseBatchExtractor(BaseExtractor):
    """
    Extractores por lotes para fuentes grandes.

    Extrae datos en lotes para mejor manejo de memoria.
    """

    def __init__(self, batch_size: int = 1000):
        """
        Inicializa el extractor por lotes.

        Args:
            batch_size: Tamaño de cada lote
        """
        self.batch_size = batch_size

    @abstractmethod
    def extract_batch(self, skip: int = 0, limit: int = None) -> List[str]:
        """
        Extrae un lote específico de datos.

        Args:
            skip: Número de líneas a saltar
            limit: Máximo de líneas a extraer (None para tamaño de lote)

        Returns:
            List[str]: Lote de datos extraídos
        """

    def extract_all_batches(self) -> Iterator[List[str]]:
        """
        Extrae todos los datos en lotes secuenciales.

        Yields:
            List[str]: Lotes de datos
        """
        offset = 0
        while True:
            batch = self.extract_batch(skip=offset, limit=self.batch_size)
            if not batch:
                break
            yield batch
            offset += len(batch)

    def get_total_batches(self) -> Optional[int]:
        """
        Obtiene el número total de lotes.

        Returns:
            Optional[int]: Número total de lotes o None si no se puede determinar
        """
        total_size = self.get_size_estimate()
        if total_size and self.batch_size:
            # Estimación basada en tamaño promedio por línea
            return (total_size // (self.batch_size * 80)) + 1
        return None
