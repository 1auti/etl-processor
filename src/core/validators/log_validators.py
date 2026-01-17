"""
Log format and record validators.
"""

import re
import json
from typing import Dict, Any, List


def validate_log_format(log_line: str, format_type: str = 'apache') -> bool:
    """Valida el formato de una línea de log."""
    if not log_line or not isinstance(log_line, str):
        return False

    log_line = log_line.strip()

    if format_type == 'json':
        try:
            json.loads(log_line)
            return True
        except json.JSONDecodeError:
            return False

    elif format_type == 'apache':
        apache_pattern = r'^(\S+) (\S+) (\S+) \[([^\]]+)\] "(\S+) (\S+) (\S+)" (\d+) (\d+)$'
        return bool(re.match(apache_pattern, log_line))

    elif format_type == 'nginx':
        nginx_pattern = r'^(\S+) - (\S+) \[([^\]]+)\] "(\S+) (\S+) (\S+)" (\d+) (\d+)'
        return bool(re.match(nginx_pattern, log_line))

    else:
        return bool(log_line)


def validate_log_record(record: Dict[str, Any]) -> List[str]:
    """Valida un registro de log parseado."""
    errors = []

    from .ip_validators import validate_ip_address
    from .http_validators import validate_http_method, validate_http_status
    from .timestamp_validators import validate_timestamp
    from .url_validators import validate_url

    required_fields = ['timestamp', 'ip_address', 'http_method', 'url', 'status_code']

    for field in required_fields:
        if field not in record:
            errors.append(f"Missing required field: {field}")

    if 'ip_address' in record:
        if not validate_ip_address(record['ip_address']):
            errors.append(f"Invalid IP address: {record['ip_address']}")

    if 'http_method' in record:
        if not validate_http_method(record['http_method']):
            errors.append(f"Invalid HTTP method: {record['http_method']}")

    if 'status_code' in record:
        if not validate_http_status(record['status_code']):
            errors.append(f"Invalid HTTP status: {record['status_code']}")

    if 'timestamp' in record:
        if not validate_timestamp(record['timestamp']):
            errors.append(f"Invalid timestamp: {record['timestamp']}")

    if 'url' in record:
        if not validate_url(record['url']):
            errors.append(f"Invalid URL: {record['url']}")

    return errors
