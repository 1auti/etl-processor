"""
Decorators for automatic metric collection.
"""

import functools
import time
from typing import Callable, Optional

from src.core.logger import get_logger

from .registry import MetricsRegistry
from .types import MetricLevel, MetricType, TagsDict

logger = get_logger(__name__)


def metrics_timer(
    metric_name: str,
    collector_name: str = "default",
    record_on_error: bool = True,
    additional_tags: Optional[TagsDict] = None,
):
    """
    Decorator to measure execution time.

    Example:
        @metrics_timer("api.request_duration")
        def handle_request():
            # code...
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            success = False

            try:
                result = func(*args, **kwargs)
                success = True
                return result

            finally:
                duration = time.perf_counter() - start_time

                if success or record_on_error:
                    collector = MetricsRegistry.get_collector(collector_name)

                    tags = {
                        "function": func.__name__,
                        "module": func.__module__,
                        "success": str(success),
                    }

                    if additional_tags:
                        tags.update(additional_tags)

                    # Add class name if method
                    if args and hasattr(args[0], "__class__"):
                        tags["class"] = args[0].__class__.__name__

                    collector.record_metric(
                        name=f"{metric_name}.duration",
                        value=duration,
                        metric_type=MetricType.TIMER,
                        tags=tags,
                        unit="seconds",
                    )

                    # Record success rate
                    collector.record_metric(
                        name=f"{metric_name}.success",
                        value=1.0 if success else 0.0,
                        metric_type=MetricType.GAUGE,
                        tags=tags,
                    )

        return wrapper

    return decorator


def metrics_counter(
    metric_name: str,
    collector_name: str = "default",
    increment: int = 1,
    tags: Optional[TagsDict] = None,
):
    """
    Decorator to count function executions.

    Example:
        @metrics_counter("api.requests")
        def handle_request():
            # code...
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            collector = MetricsRegistry.get_collector(collector_name)

            current_tags = tags.copy() if tags else {}
            current_tags.update({"function": func.__name__, "module": func.__module__})

            collector.record_metric(
                name=f"{metric_name}.count",
                value=increment,
                metric_type=MetricType.COUNTER,
                tags=current_tags,
            )

            return func(*args, **kwargs)

        return wrapper

    return decorator


def metrics_error_counter(
    metric_name: str,
    collector_name: str = "default",
    exceptions: tuple = (Exception,),
    tags: Optional[TagsDict] = None,
):
    """
    Decorator to count specific exceptions.

    Example:
        @metrics_error_counter("api.errors")
        def risky_operation():
            # code that might raise...
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                collector = MetricsRegistry.get_collector(collector_name)

                current_tags = tags.copy() if tags else {}
                current_tags.update(
                    {
                        "function": func.__name__,
                        "error_type": type(e).__name__,
                        "error_message": str(e)[:100],
                    }
                )

                collector.record_metric(
                    name=f"{metric_name}.error_count",
                    value=1,
                    metric_type=MetricType.COUNTER,
                    tags=current_tags,
                    level=MetricLevel.ERROR,
                )
                raise

        return wrapper

    return decorator
