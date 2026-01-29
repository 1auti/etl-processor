"""
Main package exception export

Este módulo centraliza todas las exportaciones de excepciones del sistema ETL.
Proporciona una API unificada para el manejo de errores.
"""

# Import from subpackages
from .checkpoint import CheckpointCorruptedError, CheckpointError, CheckpointNotFoundError
from .configuration import ConfigurationError, InvalidConfigError, MissingConfigError
from .enrichment import EnrichmentError, GeoIpLookupError, UserAgentParseError
from .etl_exception import EtlException
from .file import FileAlredyProcessedError, FileCorruptedError, FileError, FilePermissionError
from .metrics import (
    MetricsAggregationError,
    MetricsBufferError,
    MetricsConfigurationError,
    MetricsConnectionError,
    MetricsError,
    MetricsStorageError,
    MetricsValidationError,
)
from .parsing import InvalidLogFormatError, ParsingError, UnsupportedLogFormatError
from .processing import BatchProcessingError, PipelineError, ProcessingError
from .retry import RetryExhaustedError
from .storage import (
    DatabaseConnectionError,
    DatabaseInsertError,
    DatabaseQueryError,
    StorageError,
    TransactionError,
)
from .utility import utility_error
from .validation import (
    InvalidHttpMethodError,
    InvalidIpAddresError,
    InvalidStatusCodeError,
    InvalidTimestampError,
    SuspiciousPatternError,
    ValidationError,
    invalidUrlError,
)

# Re-export everything
__all__ = [
    # Exception base
    "EtlException",
    # Checkpoint exceptions
    "CheckpointCorruptedError",
    "CheckpointError",
    "CheckpointNotFoundError",
    # Config exceptions
    "ConfigurationError",
    "InvalidConfigError",
    "MissingConfigError",
    # Enrichment exceptions
    "EnrichmentError",
    "GeoIpLookupError",
    "UserAgentParseError",
    # File exceptions
    "FileAlredyProcessedError",
    "FileCorruptedError",
    "FileError",
    "FilePermissionError",
    # Log exceptions
    "InvalidLogFormatError",
    "ParsingError",
    "UnsupportedLogFormatError",
    # Processing exceptions
    "BatchProcessingError",
    "PipelineError",
    "ProcessingError",
    # Retry exceptions
    "RetryExhaustedError",
    # Storage exceptions
    "DatabaseConnectionError",
    "DatabaseInsertError",
    "DatabaseQueryError",  # Corregido de DatabaeQueryError
    "StorageError",
    "TransactionError",
    # Utility exceptions
    "utility_error",
    # Validation exceptions
    "InvalidHttpMethodError",
    "InvalidIpAddresError",
    "InvalidStatusCodeError",
    "InvalidTimestampError",
    "invalidUrlError",
    "SuspiciousPatternError",
    "ValidationError"
    # Metrics exceptions
    "MetricsAggregationError",
    "MetricsBufferError",
    "MetricsConfigurationError",
    "MetricsConnectionError",
    "MetricsError",
    "MetricsStorageError",
    "MetricsValidationError",
]

# Grupos de excepciones para importación selectiva
CHECKPOINT_EXCEPTIONS = [
    "CheckpointCorruptedError",
    "CheckpointError",
    "CheckpointNotFoundError",
]

CONFIG_EXCEPTIONS = [
    "ConfigurationError",
    "InvalidConfigError",
    "MissingConfigError",
]

ENRICHMENT_EXCEPTIONS = [
    "EnrichmentError",
    "GeoIpLookupError",
    "UserAgentParseError",
]

FILE_EXCEPTIONS = [
    "FileAlredyProcessedError",
    "FileCorruptedError",
    "FileError",
    "FilePermissionError",
]

LOG_EXCEPTIONS = [
    "InvalidLogFormatError",
    "ParsingError",
    "UnsupportedLogFormatError",
]

PROCESSING_EXCEPTIONS = [
    "BatchProcessingError",
    "PipelineError",
    "ProcessingError",
]

STORAGE_EXCEPTIONS = [
    "DatabaseConnectionError",
    "DatabaseInsertError",
    "DatabaseQueryError",
    "StorageError",
    "TransactionError",
]

VALIDATION_EXCEPTIONS = [
    "InvalidHttpMethodError",
    "InvalidIpAddresError",
    "InvalidStatusCodeError",
    "InvalidTimestampError",
    "invalidUrlError",
    "SuspiciousPatternError",
    "ValidationError",
]

# Diccionario con todos los grupos (útil para documentación)
EXCEPTION_GROUPS = {
    "checkpoint": CHECKPOINT_EXCEPTIONS,
    "config": CONFIG_EXCEPTIONS,
    "enrichment": ENRICHMENT_EXCEPTIONS,
    "file": FILE_EXCEPTIONS,
    "log": LOG_EXCEPTIONS,
    "processing": PROCESSING_EXCEPTIONS,
    "storage": STORAGE_EXCEPTIONS,
    "validation": VALIDATION_EXCEPTIONS,
}
