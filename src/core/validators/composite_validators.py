"""
Composite validators for common use cases.
"""

from typing import Any, Dict, List

from .http_validators import validate_http_method, validate_http_status
from .ip_validators import validate_ip_address
from .schema_validators import validate_schema
from .timestamp_validators import validate_timestamp
from .url_validators import validate_http_url, validate_url


class LogRecordValidator:
    """Composite validator for log records."""

    LOG_SCHEMA = {
        "timestamp": {"type": str, "required": True},
        "ip_address": {"type": str, "required": True},
        "http_method": {"type": str, "required": True},
        "url": {"type": str, "required": True},
        "status_code": {"type": int, "required": True},
        "user_agent": {"type": str, "required": False},
        "referrer": {"type": str, "required": False},
        "response_size": {"type": int, "required": False, "min": 0},
        "processing_time": {"type": float, "required": False, "min": 0},
    }

    def __init__(self, strict: bool = True):
        self.strict = strict

    def validate(self, record: Dict[str, Any]) -> List[str]:
        """Validate a log record."""
        errors = []

        # Schema validation
        schema_errors = validate_schema(record, self.LOG_SCHEMA)
        errors.extend(schema_errors)

        if errors and self.strict:
            return errors

        # Semantic validation
        if "timestamp" in record:
            if not validate_timestamp(record["timestamp"]):
                errors.append(f"Invalid timestamp format: {record['timestamp']}")

        if "ip_address" in record:
            if not validate_ip_address(record["ip_address"]):
                errors.append(f"Invalid IP address: {record['ip_address']}")

        if "http_method" in record:
            if not validate_http_method(record["http_method"]):
                errors.append(f"Invalid HTTP method: {record['http_method']}")

        if "status_code" in record:
            if not validate_http_status(record["status_code"]):
                errors.append(f"Invalid HTTP status code: {record['status_code']}")

        if "url" in record:
            if not validate_http_url(record["url"]):
                errors.append(f"Invalid URL: {record['url']}")

        return errors

    def is_valid(self, record: Dict[str, Any]) -> bool:
        """Check if record is valid."""
        return len(self.validate(record)) == 0


class NetworkValidator:
    """Composite validator for network-related data."""

    def validate_ip_with_metadata(self, ip_string: str) -> Dict[str, Any]:
        """Validate IP and return metadata."""
        result = {
            "valid": False,
            "version": None,
            "is_private": False,
            "is_public": False,
            "errors": [],
        }

        if not validate_ip_address(ip_string):
            result["errors"].append(f"Invalid IP address: {ip_string}")
            return result

        result["valid"] = True

        try:
            import ipaddress

            ip = ipaddress.ip_address(ip_string)

            if isinstance(ip, ipaddress.IPv4Address):
                result["version"] = 4
            else:
                result["version"] = 6

            result["is_private"] = ip.is_private
            result["is_public"] = ip.is_global and not ip.is_private

        except Exception as e:
            result["errors"].append(f"Error analyzing IP: {e}")

        return result

    def validate_url_with_components(self, url_string: str) -> Dict[str, Any]:
        """Validate URL and return parsed components."""
        from urllib.parse import urlparse

        result = {
            "valid": False,
            "scheme": None,
            "netloc": None,
            "path": None,
            "query": None,
            "fragment": None,
            "errors": [],
        }

        if not validate_url(url_string):
            result["errors"].append(f"Invalid URL: {url_string}")
            return result

        result["valid"] = True

        try:
            parsed = urlparse(url_string)
            result["scheme"] = parsed.scheme
            result["netloc"] = parsed.netloc
            result["path"] = parsed.path
            result["query"] = parsed.query
            result["fragment"] = parsed.fragment

        except Exception as e:
            result["errors"].append(f"Error parsing URL: {e}")

        return result


class ConfigValidator:
    """Composite validator for configuration."""

    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema

    def validate(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate configuration with detailed results."""
        result = {"valid": False, "errors": [], "warnings": [], "missing": [], "invalid": []}

        # Check required fields
        for field_name, field_schema in self.schema.items():
            is_required = field_schema.get("required", False)

            if is_required and field_name not in config:
                result["missing"].append(field_name)

        if result["missing"]:
            result["errors"].extend(
                [f"Missing required field: {field}" for field in result["missing"]]
            )
            return result

        # Validate each field
        for field_name, field_value in config.items():
            if field_name not in self.schema:
                result["warnings"].append(f"Unknown field: {field_name}")
                continue

            field_schema = self.schema[field_name]
            field_errors = self._validate_field(field_name, field_value, field_schema)

            if field_errors:
                result["invalid"].append(field_name)
                result["errors"].extend(field_errors)

        result["valid"] = len(result["errors"]) == 0
        return result

    def _validate_field(self, field_name: str, value: Any, schema: Dict[str, Any]) -> List[str]:
        """Validate a single field."""
        errors = []

        expected_type = schema.get("type")
        if expected_type and not isinstance(value, expected_type):
            errors.append(
                f"{field_name}: Expected type {expected_type.__name__}, got {type(value).__name__}"
            )

        if isinstance(value, (int, float)):
            min_val = schema.get("min")
            max_val = schema.get("max")

            if min_val is not None and value < min_val:
                errors.append(f"{field_name}: Value {value} is less than minimum {min_val}")

            if max_val is not None and value > max_val:
                errors.append(f"{field_name}: Value {value} is greater than maximum {max_val}")

        return errors
