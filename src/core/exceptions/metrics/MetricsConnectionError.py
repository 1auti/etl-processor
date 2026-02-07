from src.core.exceptions.metrics.MetricsError import MetricsError


class MetricsConnectionError(MetricsError):
    """Error connecting to metrics storage."""
