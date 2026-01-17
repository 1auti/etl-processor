"""
Clases base abstractas para procesadores ETL completos.

Los procesadores ETL orquestan el flujo completo de:
1. EXTRACCIÓN: Obtener datos de fuentes
2. TRANSFORMACIÓN: Convertir y limpiar datos
3. CARGA: Almacenar datos procesados en destinos
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime

from .types import (
    LogRecordBatch,
    ProcessStats,
    ProcessingResult,
    ProcessingStatus
)


class BaseETLProcessor(ABC):
    """
    Clase base abstracta para procesadores ETL completos.

    Implementa el patrón Template Method, donde `run()` define el esqueleto
    del proceso y las subclases implementan los pasos concretos.
    """

    def __init__(self, name: str = "procesador_sin_nombre"):
        """
        Inicializa el procesador ETL.

        Args:
            name: Nombre del procesador para logging y monitoreo
        """
        self.name = name
        self.stats: ProcessStats = {
            'processor_name': name,
            'status': ProcessingStatus.PENDING.value,
            'start_time': None,
            'end_time': None,
            'total_lines': 0,
            'parsed_successfully': 0,
            'parse_errors': 0,
            'inserted': 0,
            'warnings': [],
            'errors': []
        }

    @property
    @abstractmethod
    def version(self) -> str:
        """
        Versión de la implementación del procesador.

        Returns:
            str: Versión semántica (ej: '1.0.0', '2.1.3')
        """
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """
        Descripción del propósito del procesador.

        Returns:
            str: Descripción breve del procesador
        """
        pass

    @abstractmethod
    def initialize(self) -> bool:
        """
        Inicializa recursos necesarios antes del procesamiento.

        Returns:
            bool: True si la inicialización fue exitosa

        Raises:
            InitializationError: Si falla la inicialización
        """
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """
        Libera recursos después del procesamiento.

        Debe llamarse después de `run()`, incluso si hay errores.
        """
        pass

    @abstractmethod
    def extract(self) -> List[str]:
        """
        Fase de EXTRACCIÓN - obtiene datos crudos de la fuente.

        Returns:
            List[str]: Lista de líneas/datos crudos extraídos

        Raises:
            ExtractionError: Si falla la extracción de datos
            SourceUnavailableError: Si la fuente no está disponible
        """
        pass

    @abstractmethod
    def transform(self, data: List[str]) -> LogRecordBatch:
        """
        Fase de TRANSFORMACIÓN - convierte datos crudos en registros estructurados.

        Args:
            data: Datos crudos a transformar

        Returns:
            LogRecordBatch: Registros transformados y validados

        Raises:
            TransformationError: Si falla la transformación
            ValidationError: Si los datos no pasan la validación
        """
        pass

    @abstractmethod
    def load(self, records: LogRecordBatch) -> int:
        """
        Fase de CARGA - guarda registros en el destino.

        Args:
            records: Registros transformados a guardar

        Returns:
            int: Número de registros cargados exitosamente

        Raises:
            LoadError: Si falla la carga de datos
            DestinationError: Si el destino no está disponible
        """
        pass

    def run_with_context(self) -> ProcessingResult:
        """
        Ejecuta el proceso ETL con manejo automático de inicialización y limpieza.

        Returns:
            ProcessingResult: Resultado del procesamiento
        """
        try:
            # Inicializar recursos
            if not self.initialize():
                return ProcessingResult(
                    success=False,
                    records_processed=0,
                    errors=1,
                    duration_seconds=0.0,
                    status=ProcessingStatus.FAILED,
                    message="Error en inicialización del procesador",
                    details={'processor': self.name, 'stage': 'initialization'}
                )

            # Ejecutar procesamiento principal
            return self.run()

        finally:
            # Siempre limpiar recursos
            self.cleanup()

    def run(self) -> ProcessingResult:
        """
        Ejecuta el proceso ETL completo (Template Method).

        Returns:
            ProcessingResult: Resultado estructurado del procesamiento
        """
        self.stats['status'] = ProcessingStatus.PROCESSING.value
        self.stats['start_time'] = datetime.now()

        try:
            # 1. EXTRACCIÓN
            raw_data = self.extract()
            self.stats['total_lines'] = len(raw_data)
            self._log_progress("Extracción completada", lines=len(raw_data))

            # 2. TRANSFORMACIÓN
            transformed_data = self.transform(raw_data)
            self.stats['parsed_successfully'] = len(transformed_data)
            self.stats['parse_errors'] = self.stats['total_lines'] - len(transformed_data)
            self._log_progress(
                "Transformación completada",
                parsed=len(transformed_data),
                errors=self.stats['parse_errors']
            )

            # 3. CARGA
            loaded_count = self.load(transformed_data)
            self.stats['inserted'] = loaded_count
            self._log_progress("Carga completada", inserted=loaded_count)

            # Resultado exitoso
            duration = self.get_duration()
            self.stats['status'] = ProcessingStatus.COMPLETED.value

            return ProcessingResult(
                success=True,
                records_processed=loaded_count,
                errors=self.stats['parse_errors'],
                duration_seconds=duration if duration else 0.0,
                status=ProcessingStatus.COMPLETED,
                message="Procesamiento ETL completado exitosamente",
                details={
                    'processor': self.name,
                    'version': self.version,
                    'extracted': self.stats['total_lines'],
                    'transformed': self.stats['parsed_successfully'],
                    'loaded': loaded_count,
                    'efficiency': loaded_count / max(1, self.stats['total_lines'])
                }
            )

        except Exception as e:
            # Manejo de errores
            self.stats['status'] = ProcessingStatus.FAILED.value
            self.stats['errors'].append(str(e))

            duration = self.get_duration()

            return ProcessingResult(
                success=False,
                records_processed=self.stats.get('inserted', 0),
                errors=self.stats.get('parse_errors', 0) + 1,
                duration_seconds=duration if duration else 0.0,
                status=ProcessingStatus.FAILED,
                message=f"Error en procesamiento ETL: {str(e)}",
                details={
                    'error_type': type(e).__name__,
                    'processor': self.name,
                    'stage': self._get_failed_stage(e),
                    'extracted': self.stats.get('total_lines', 0),
                    'transformed': self.stats.get('parsed_successfully', 0),
                    'loaded': self.stats.get('inserted', 0)
                }
            )

        finally:
            self.stats['end_time'] = datetime.now()

    def get_duration(self) -> Optional[float]:
        """
        Calcula la duración del procesamiento en segundos.

        Returns:
            Optional[float]: Duración en segundos, o None si no ha finalizado
        """
        if self.stats['start_time'] and self.stats['end_time']:
            delta = self.stats['end_time'] - self.stats['start_time']
            return delta.total_seconds()
        return None

    def get_stats(self) -> ProcessStats:
        """
        Obtiene estadísticas actuales del procesamiento.

        Returns:
            ProcessStats: Diccionario con estadísticas
        """
        return self.stats.copy()

    def get_summary(self) -> Dict[str, Any]:
        """
        Obtiene un resumen ejecutivo del procesamiento.

        Returns:
            Dict[str, Any]: Resumen con métricas clave
        """
        duration = self.get_duration()

        summary = {
            'processor': self.name,
            'version': self.version,
            'description': self.description,
            'status': self.stats['status'],
            'total_lines': self.stats['total_lines'],
            'successfully_parsed': self.stats['parsed_successfully'],
            'parse_success_rate': (
                self.stats['parsed_successfully'] / max(1, self.stats['total_lines'])
            ),
            'loaded': self.stats['inserted'],
            'load_success_rate': (
                self.stats['inserted'] / max(1, self.stats['parsed_successfully'])
            ),
            'total_errors': self.stats['parse_errors'] + len(self.stats['errors']),
            'warnings': len(self.stats['warnings']),
        }

        if duration is not None:
            summary.update({
                'duration_seconds': duration,
                'lines_per_second': self.stats['total_lines'] / duration if duration > 0 else 0,
                'records_per_second': self.stats['inserted'] / duration if duration > 0 else 0,
            })

        return summary

    def health_check(self) -> Dict[str, Any]:
        """
        Realiza un chequeo de salud del procesador.

        Returns:
            Dict[str, Any]: Estado de salud del procesador
        """
        return {
            'processor': self.name,
            'version': self.version,
            'status': self.stats['status'],
            'last_run_duration': self.get_duration(),
            'total_runs': self.stats.get('run_count', 0),
            'total_processed': self.stats.get('total_lines', 0),
            'success_rate': self._calculate_success_rate(),
            'ready': self._is_ready(),
        }

    # Métodos protegidos para uso interno
    def _log_progress(self, message: str, **kwargs):
        """
        Registra el progreso del procesamiento.

        Args:
            message: Mensaje de progreso
            **kwargs: Datos adicionales para logging
        """
        # Este método debería integrarse con tu sistema de logging
        progress_data = {
            'timestamp': datetime.now().isoformat(),
            'processor': self.name,
            'message': message,
            **kwargs,
            'stats': self.stats.copy()
        }
        # Aquí iría la llamada a tu logger
        # logger.info("Progreso ETL", **progress_data)

    def _get_failed_stage(self, error: Exception) -> str:
        """
        Determina en qué fase falló el procesamiento basado en las estadísticas.

        Args:
            error: Excepción que causó el fallo

        Returns:
            str: Fase donde ocurrió el error ('extract', 'transform', 'load', 'unknown')
        """
        if self.stats['total_lines'] == 0:
            return 'extract'
        elif self.stats['parsed_successfully'] == 0 and self.stats['total_lines'] > 0:
            return 'transform'
        elif self.stats['inserted'] == 0 and self.stats['parsed_successfully'] > 0:
            return 'load'
        else:
            return 'unknown'

    def _calculate_success_rate(self) -> float:
        """Calcula la tasa de éxito histórica."""
        total = self.stats.get('total_lines', 0)
        success = self.stats.get('inserted', 0)
        return success / max(1, total)

    def _is_ready(self) -> bool:
        """Verifica si el procesador está listo para ejecutarse."""
        return self.stats['status'] in [
            ProcessingStatus.PENDING.value,
            ProcessingStatus.COMPLETED.value
        ]


class BaseParallelETLProcessor(BaseETLProcessor):
    """
    Procesador ETL con soporte para procesamiento paralelo.

    Extiende el procesador base para manejar múltiples fuentes
    o lotes de datos en paralelo.
    """

    @abstractmethod
    def get_parallel_workers(self) -> int:
        """
        Obtiene el número de workers para procesamiento paralelo.

        Returns:
            int: Número de workers paralelos
        """
        pass

    @abstractmethod
    def split_data_for_parallel(self, data: List[str]) -> List[List[str]]:
        """
        Divide los datos para procesamiento paralelo.

        Args:
            data: Datos completos a dividir

        Returns:
            List[List[str]]: Lista de lotes para procesar en paralelo
        """
        pass

    @abstractmethod
    def merge_results(self, results: List[LogRecordBatch]) -> LogRecordBatch:
        """
        Fusiona resultados de procesamiento paralelo.

        Args:
            results: Resultados de todos los workers

        Returns:
            LogRecordBatch: Resultados fusionados
        """
        pass


class BaseIncrementalETLProcessor(BaseETLProcessor):
    """
    Procesador ETL con soporte para procesamiento incremental.

    Mantiene estado entre ejecuciones para procesar solo datos nuevos.
    """

    @abstractmethod
    def get_last_processed_checkpoint(self) -> Optional[Dict[str, Any]]:
        """
        Obtiene el último checkpoint procesado.

        Returns:
            Optional[Dict[str, Any]]: Checkpoint o None si es primera ejecución
        """
        pass

    @abstractmethod
    def save_checkpoint(self, checkpoint_data: Dict[str, Any]) -> bool:
        """
        Guarda un nuevo checkpoint después del procesamiento.

        Args:
            checkpoint_data: Datos del checkpoint

        Returns:
            bool: True si se guardó exitosamente
        """
        pass

    @abstractmethod
    def extract_since_checkpoint(self, checkpoint: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        Extrae solo datos nuevos desde el último checkpoint.

        Args:
            checkpoint: Checkpoint opcional

        Returns:
            List[str]: Datos nuevos a procesar
        """
        pass
