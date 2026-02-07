"""
Global metrics registry for easy access to collectors.
Singleton pattern for shared metrics collection.
"""

from typing import Any, Dict

from core import logger
from src.core.exceptions import MetricsError

from .collector import AdvancedMetricsCollector


class MetricsRegistry:
    """
    Global registry for metrics collectors.
    Provides singleton access to configured collectors.
    """

    _instance = None
    _collectors: Dict[str, AdvancedMetricsCollector] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def register_collector(
        cls, name: str, db_config: Dict[str, Any], **kwargs
    ) -> AdvancedMetricsCollector:
        """Register a new collector."""
        from .validators import validate_db_config

        validate_db_config(db_config)

        collector = AdvancedMetricsCollector(db_config, **kwargs)
        cls._collectors[name] = collector
        return collector

    @classmethod
    def get_collector(cls, name: str = "default") -> AdvancedMetricsCollector:
        """Get a registered collector."""
        if name not in cls._collectors:
            raise MetricsError(f"Collector '{name}' not registered")
        return cls._collectors[name]

    @classmethod
    def record_metric(cls, name: str, *args, **kwargs) -> None:
        """Record metric to default collector."""
        collector = cls.get_collector("default")
        collector.record_metric(name, *args, **kwargs)

    @classmethod
    def get_all_collectors(cls) -> Dict[str, AdvancedMetricsCollector]:
        """Get all registered collectors."""
        return cls._collectors.copy()

    @classmethod
    def flush_all(cls) -> None:
        """Flush all collectors."""
        for collector in cls._collectors.values():
            try:
                collector.flush(force=True)
            except Exception as e:
                logger.error(f"Error flushing collector: {e}")
