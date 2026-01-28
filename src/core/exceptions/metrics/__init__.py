"""
Excepciones específicas para el sistema de métricas.

Este módulo contiene todas las excepciones personalizadas relacionadas
con la colección, almacenamiento y procesamiento de métricas.
"""

from .MetricsAggregationError import MetricsAggregationError
from .MetricsBufferError import MetricsBufferError
from .MetricsConfigurationError import MetricsConfigurationError
from .MetricsConnectionError import MetricsConnectionError
from .MetricsError import MetricsError
from .MetricsStorageError import MetricsStorageError
from .MetricsValidationError import MetricsValidationError

__all__ = [
    "MetricsAggregationError",
    "MetricsBufferError",
    "MetricsConfigurationError",
    "MetricsError",
    "MetricsConnectionError",
    "MetricsValidationError",
    "MetricsStorageError",
]
