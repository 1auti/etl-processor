"""
Timestamp and date validators.
"""

from datetime import datetime
from typing import Optional, Union

# Formatos de timestamp comunes
TIMESTAMP_FORMATS = [
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%S.%f",
    "%Y-%m-%dT%H:%M:%S%z",
    "%d/%b/%Y:%H:%M:%S %z",
    "%a, %d %b %Y %H:%M:%S %Z",
    "%Y%m%d%H%M%S",
    "%s",
]


def validate_timestamp(
    timestamp: Union[str, int, float], format_hint: Optional[str] = None
) -> bool:
    """Valida un timestamp en múltiples formatos."""
    if timestamp is None:
        return False

    if isinstance(timestamp, (int, float)):
        try:
            return 946684800 <= timestamp <= 4102444800
        except (ValueError, TypeError):
            return False

    if isinstance(timestamp, str):
        formats_to_try = []

        if format_hint:
            formats_to_try.append(format_hint)

        formats_to_try.extend(TIMESTAMP_FORMATS)

        for fmt in formats_to_try:
            try:
                datetime.strptime(timestamp, fmt)
                return True
            except ValueError:
                continue

        try:
            datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            return True
        except ValueError:
            pass

    return False


def parse_timestamp(
    timestamp: Union[str, int, float], format_hint: Optional[str] = None
) -> Optional[datetime]:
    """Parsea un timestamp a datetime."""
    if timestamp is None:
        return None

    if isinstance(timestamp, (int, float)):
        try:
            return datetime.fromtimestamp(timestamp)
        except (ValueError, TypeError):
            return None

    if isinstance(timestamp, str):
        formats_to_try = []

        if format_hint:
            formats_to_try.append(format_hint)

        formats_to_try.extend(TIMESTAMP_FORMATS)

        for fmt in formats_to_try:
            try:
                return datetime.strptime(timestamp, fmt)
            except ValueError:
                continue

        try:
            return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError:
            pass

    return None


def validate_timestamp_range(
    timestamp: Union[str, int, float, datetime],
    start_date: Optional[Union[str, int, float, datetime]] = None,
    end_date: Optional[Union[str, int, float, datetime]] = None,
) -> bool:
    """Valida que un timestamp esté dentro de un rango."""
    ts_dt = parse_timestamp(timestamp) if not isinstance(timestamp, datetime) else timestamp
    start_dt = (
        parse_timestamp(start_date)
        if start_date and not isinstance(start_date, datetime)
        else start_date
    )
    end_dt = (
        parse_timestamp(end_date) if end_date and not isinstance(end_date, datetime) else end_date
    )

    if ts_dt is None:
        return False

    if start_dt and ts_dt < start_dt:
        return False

    if end_dt and ts_dt > end_dt:
        return False

    return True
