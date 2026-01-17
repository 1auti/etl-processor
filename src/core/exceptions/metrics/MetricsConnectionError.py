from core.exceptions.metrics import MetricsError


class MetricsConnectionError(MetricsError):
    """Error connecting to metrics storage."""
    pass
