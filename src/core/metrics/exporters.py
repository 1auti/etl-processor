"""
Export metrics to different formats.
"""

import json
from typing import Dict, Any, List
from datetime import datetime, timedelta
from .registry import MetricsRegistry
from .types import Metric, MetricType


class PrometheusExporter:
    """Export metrics to Prometheus format."""

    @staticmethod
    def export(collector_name: str = "default", hours: int = 1) -> str:
        """Export to Prometheus format."""
        collector = MetricsRegistry.get_collector(collector_name)

        # This would query the database and format for Prometheus
        # Implementation depends on your storage

        lines = [
            '# HELP etl_processed_records Total records processed',
            '# TYPE etl_processed_records counter',
            'etl_processed_records 1500',
            '',
            '# HELP etl_processing_duration_seconds Processing duration',
            '# TYPE etl_processing_duration_seconds histogram',
            'etl_processing_duration_seconds_bucket{le="0.1"} 10',
            'etl_processing_duration_seconds_bucket{le="0.5"} 50',
            'etl_processing_duration_seconds_bucket{le="1.0"} 100',
            'etl_processing_duration_seconds_bucket{le="+Inf"} 150',
            'etl_processing_duration_seconds_sum 75.5',
            'etl_processing_duration_seconds_count 150'
        ]

        return "\n".join(lines)


class JSONExporter:
    """Export metrics to JSON format."""

    @staticmethod
    def export(collector_name: str = "default", **filters) -> Dict[str, Any]:
        """Export to JSON format."""
        collector = MetricsRegistry.get_collector(collector_name)

        # Get metrics summary
        summary = collector.get_metrics_summary(**filters)

        return {
            'exported_at': datetime.now().isoformat(),
            'format': 'json',
            'filters': filters,
            'data': summary
        }


class ConsoleExporter:
    """Export metrics to console for debugging."""

    @staticmethod
    def export(collector_name: str = "default") -> str:
        """Pretty print metrics to console."""
        collector = MetricsRegistry.get_collector(collector_name)
        stats = collector.get_stats()

        output = []
        output.append("=" * 50)
        output.append("METRICS COLLECTOR STATISTICS")
        output.append("=" * 50)

        for key, value in stats['collector'].items():
            output.append(f"{key}: {value}")

        output.append("\nAGGREGATES:")
        for name, agg in stats['aggregates'].items():
            output.append(f"  {name}:")
            output.append(f"    count: {agg['count']}")
            output.append(f"    avg: {agg['avg']:.2f}")

        return "\n".join(output)
