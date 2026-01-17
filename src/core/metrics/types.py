"""
Type definitions for the metrics system.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Union
from datetime import datetime


class MetricType(str, Enum):
    """Tipos de métricas soportados."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    SUMMARY = "summary"
    RATE = "rate"


class MetricLevel(str, Enum):
    """Niveles de importancia."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


# Type aliases
MetricValue = Union[int, float]
TagsDict = Dict[str, Union[str, int, float, bool]]


@dataclass
class Metric:
    """Representa una métrica individual."""
    name: str
    value: MetricValue
    metric_type: MetricType
    timestamp: datetime
    tags: TagsDict
    level: MetricLevel = MetricLevel.INFO
    description: Optional[str] = None
    source: Optional[str] = None
    unit: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serializa a diccionario."""
        return {
            'name': self.name,
            'value': float(self.value),
            'metric_type': self.metric_type.value,
            'timestamp': self.timestamp.isoformat(),
            'tags': self.tags,
            'level': self.level.value,
            'description': self.description,
            'source': self.source,
            'unit': self.unit,
            'metadata': self.metadata
        }


@dataclass
class MetricAggregate:
    """Agregación de múltricas para análisis."""
    name: str
    metric_type: MetricType
    count: int = 0
    sum: float = 0.0
    min: float = float('inf')
    max: float = float('-inf')
    avg: float = 0.0
    last_value: Optional[float] = None
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None

    def update(self, metric: Metric) -> None:
        """Actualiza con nueva métrica."""
        self.count += 1
        self.sum += metric.value

        if metric.value < self.min:
            self.min = metric.value
        if metric.value > self.max:
            self.max = metric.value

        self.avg = self.sum / self.count
        self.last_value = metric.value

        if not self.first_seen:
            self.first_seen = metric.timestamp
        self.last_seen = metric.timestamp
