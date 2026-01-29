"""
Logger package for the ETL system.

Provides structured logging with context, metrics, and function tracing.
All components are configured through configure_logging().
"""

from .configuration_structlog import configure_logging
from .context_manager_logger import log_context
from .decorador_logging import log_function_call
from .logger_factory import get_logger
from .logger_procesadores import add_caller_info, add_log_level, add_timestamp
from .metrics_logger import MetricsLogger

# Re-export all public functions and classes
__all__ = [
    # Configuration
    "configure_logging",
    "get_logger",
    # Decorators
    "log_function_call",
    # Context managers
    "log_context",
    # Metrics
    "MetricsLogger",
    # Processors (mainly for internal use, but available if needed)
    "add_caller_info",
    "add_log_level",
    "add_timestamp",
    # Logger factory
    "get_logger",
]
