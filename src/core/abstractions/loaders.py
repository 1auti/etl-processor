"""
Clases base abstractas para cargadores de datos.

Los cargadores (loaders) son responsables de guardar datos procesados
en varios destinos (bases de datos, archivos, APIs, etc.).
"""

from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Any, Dict, List

from .types import LogRecord, LogRecordBatch, OperationResult


class BaseLoader(ABC):
    """
    Clase base abstracta para cargadores de datos.

    Define el contrato para cargar datos procesados en destinos.
    Las implementaciones deben manejar:
    - Gestión de conexiones
    - Manejo de errores
    - Operaciones por lotes (batch)
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Nombre del cargador para logging e identificación.

        Returns:
            str: Nombre del cargador
        """

    @property
    @abstractmethod
    def supported_destinations(self) -> List[str]:
        """
        Tipos de destinos soportados por este cargador.

        Returns:
            List[str]: Tipos de destinos soportados
            Ejemplo: ['postgresql', 'csv', 'elasticsearch']
        """

    @abstractmethod
    def connect(self) -> OperationResult:
        """
        Establece conexión con el destino.

        Debe llamarse antes de cualquier operación de carga.

        Returns:
            OperationResult: (éxito, mensaje_error)
        """

    @abstractmethod
    def disconnect(self) -> None:
        """
        Cierra la conexión con el destino.

        Debe llamarse después de completar todas las operaciones de carga.
        """

    @abstractmethod
    def load_batch(self, records: LogRecordBatch) -> int:
        """
        Carga un lote de registros en el destino.

        Args:
            records: Lote de registros a cargar

        Returns:
            int: Número de registros cargados exitosamente

        Raises:
            Exception: Si la carga falla
        """

    @abstractmethod
    def create_schema(self) -> OperationResult:
        """
        Crea el esquema/tablas necesarios en el destino.

        Debe crear tablas, índices, etc. si no existen.

        Returns:
            OperationResult: (éxito, mensaje_error)
        """

    @abstractmethod
    def validate_destination(self) -> OperationResult:
        """
        Valida que el destino sea accesible y esté listo.

        Returns:
            OperationResult: (éxito, mensaje_error)
        """

    def load_single(self, record: LogRecord) -> bool:
        """
        Carga un solo registro (método de conveniencia).

        Args:
            record: Registro individual a cargar

        Returns:
            bool: True si se cargó exitosamente
        """
        try:
            loaded = self.load_batch([record])
            return loaded == 1
        except Exception:
            return False

    def get_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del cargador.

        Returns:
            Dict[str, Any]: Estadísticas como registros_cargados, errores, etc.
        """
        return {
            "loader_name": self.name,
            "records_loaded": 0,
            "batch_count": 0,
            "errors": 0,
            "last_error": None,
        }

    def health_check(self) -> Dict[str, Any]:
        """
        Realiza un chequeo de salud del cargador y destino.

        Returns:
            Dict[str, Any]: Información del estado de salud
        """
        connection_ok, connection_msg = self.validate_destination()

        return {
            "loader": self.name,
            "connection_ok": connection_ok,
            "connection_message": connection_msg,
            "destination_type": ", ".join(self.supported_destinations),
            "stats": self.get_stats(),
        }

    # Soporte para context manager para gestión automática de conexiones
    @contextmanager
    def connection_context(self):
        """
        Context manager para gestión automática de conexiones.

        Example:
            with loader.connection_context():
                loader.load_batch(records)
        """
        success, error = self.connect()
        if not success:
            raise ConnectionError(f"Error al conectar: {error}")

        try:
            yield self
        finally:
            self.disconnect()


class BaseBatchLoader(BaseLoader):
    """
    Cargador base mejorado con características de optimización por lotes.

    Añade soporte para:
    - Configuración de tamaño de lote
    - Lógica de reintentos
    - Seguimiento de estadísticas por lotes
    """

    def __init__(self, batch_size: int = 1000, max_retries: int = 3):
        """
        Inicializa el cargador por lotes.

        Args:
            batch_size: Máximo de registros por lote
            max_retries: Intentos máximos de reintento en caso de fallo
        """
        self.batch_size = batch_size
        self.max_retries = max_retries
        self._stats = {
            "total_records_loaded": 0,
            "total_batches": 0,
            "failed_batches": 0,
            "retry_count": 0,
            "connection_errors": 0,
        }

    def load_large_dataset(self, records: LogRecordBatch) -> Dict[str, Any]:
        """
        Carga un dataset grande en lotes optimizados.

        Args:
            records: Dataset completo a cargar

        Returns:
            Dict[str, Any]: Estadísticas de carga
        """
        total_records = len(records)
        total_loaded = 0
        failed_batches = []

        # Procesar en lotes
        for i in range(0, total_records, self.batch_size):
            batch = records[i : i + self.batch_size]
            batch_num = (i // self.batch_size) + 1

            try:
                loaded = self._load_with_retry(batch)
                total_loaded += loaded
                self._stats["total_batches"] += 1

            except Exception as e:
                self._stats["failed_batches"] += 1
                failed_batches.append(
                    {"batch_number": batch_num, "batch_size": len(batch), "error": str(e)}
                )

        return {
            "total_records": total_records,
            "successfully_loaded": total_loaded,
            "failed": total_records - total_loaded,
            "failed_batches": failed_batches,
            "batch_size": self.batch_size,
            "loader_stats": self._stats.copy(),
        }

    def _load_with_retry(self, batch: LogRecordBatch) -> int:
        """
        Carga un lote con lógica de reintentos.

        Args:
            batch: Lote a cargar

        Returns:
            int: Número de registros cargados exitosamente

        Raises:
            Exception: Si todos los intentos de reintento fallan
        """
        last_error = None

        for attempt in range(self.max_retries):
            try:
                return self.load_batch(batch)

            except Exception as e:
                last_error = e
                self._stats["retry_count"] += 1

                # Opcional: Agregar delay entre reintentos
                if attempt < self.max_retries - 1:
                    self._retry_delay(attempt)

        # Todos los reintentos fallaron
        raise Exception(
            f"Error al cargar lote después de {self.max_retries} intentos: {last_error}"
        )

    def _retry_delay(self, attempt: int) -> None:
        """
        Implementa backoff exponencial para reintentos.

        Args:
            attempt: Número del intento actual (comenzando en 0)
        """
        import time

        delay = min(2**attempt, 60)  # Backoff exponencial, máximo 60 segundos
        time.sleep(delay)

    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de lotes mejoradas."""
        base_stats = super().get_stats()
        base_stats.update(self._stats)
        return base_stats


class BaseTransactionalLoader(BaseBatchLoader):
    """
    Cargador con soporte transaccional.

    Proporciona capacidades de commit/rollback para consistencia de datos.
    """

    @abstractmethod
    def begin_transaction(self) -> OperationResult:
        """
        Inicia una nueva transacción.

        Returns:
            OperationResult: (éxito, mensaje_error)
        """

    @abstractmethod
    def commit(self) -> OperationResult:
        """
        Confirma (commit) la transacción actual.

        Returns:
            OperationResult: (éxito, mensaje_error)
        """

    @abstractmethod
    def rollback(self) -> OperationResult:
        """
        Revierte (rollback) la transacción actual.

        Returns:
            OperationResult: (éxito, mensaje_error)
        """

    @contextmanager
    def transaction_context(self):
        """
        Context manager para operaciones transaccionales.

        Example:
            with loader.transaction_context():
                loader.load_batch(batch1)
                loader.load_batch(batch2)
        """
        success, error = self.begin_transaction()
        if not success:
            raise Exception(f"Error al iniciar transacción: {error}")

        try:
            yield self
            success, error = self.commit()
            if not success:
                raise Exception(f"Error al confirmar transacción: {error}")

        except Exception as e:
            # Rollback en caso de cualquier excepción
            self.rollback()
            raise e
