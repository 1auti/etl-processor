"""
Metrics system for the ETL pipeline.

Provides:
- Advanced metrics collection with PostgreSQL storage
- Automatic aggregation and statistics
- Decorators for easy instrumentation
- Multiple export formats
- Global registry for easy access
"""

# Export from types
from .types import (
    Metric,
    MetricAggregate,
    MetricType,
    MetricLevel,
    MetricValue,
    TagsDict
)

# Export from collector
from .collector import AdvancedMetricsCollector

# Export from registry
from .registry import MetricsRegistry

# Export from decorators
from .decorators import (
    metrics_timer,
    metrics_counter,
    metrics_error_counter
)

# Export from exporters
from .exporters import (
    PrometheusExporter,
    JSONExporter,
    ConsoleExporter
)

# Convenience exports
__all__ = [
    # Types
    'Metric',
    'MetricAggregate',
    'MetricType',
    'MetricLevel',
    'MetricValue',
    'TagsDict',

    # Main classes
    'AdvancedMetricsCollector',
    'MetricsRegistry',

    # Decorators
    'metrics_timer',
    'metrics_counter',
    'metrics_error_counter',

    # Exporters
    'PrometheusExporter',
    'JSONExporter',
    'ConsoleExporter',
]

# Version
__version__ = '1.0.0'

# Convenience function for quick metric recording
def record_metric(name: str, value: float, **kwargs) -> None:
    """
    Quick record metric to default collector.

    Example:
        record_metric("app.started", 1, metric_type=MetricType.COUNTER)
    """
    MetricsRegistry.record_metric(name, value, **kwargs)
