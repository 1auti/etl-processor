"""
Validators module for the ETL system.

Provides specialized validators for:
- Network addresses (IPs, URLs)
- HTTP protocols and status codes
- Timestamps and date formats
- Data schemas and structures
- Configuration validation
- Log formats and records
"""

# Re-export everything from submodules
from .base import (
    get_validation_errors,
    validate_all,
    validate_any,
    validate_arguments,
    validate_with,
)
from .composite_validators import ConfigValidator, LogRecordValidator, NetworkValidator
from .config_validators import (
    _get_nested_value,
    validate_config_dict,
    validate_database_config,
    validate_env_vars,
    validate_file_paths_config,
    validate_full_config,
    validate_logging_config,
    validate_metrics_config,
    validate_processing_config,
)
from .http_validators import (
    HTTP_STATUS_CATEGORIES,
    VALID_HTTP_METHODS,
    get_http_status_category,
    validate_http_method,
    validate_http_status,
    validate_http_status_category,
)
from .ip_validators import (
    IPV4_PATTERN,
    IPV6_PATTERN,
    is_private_ip,
    is_public_ip,
    validate_ip_address,
    validate_ipv4,
    validate_ipv6,
)
from .log_validators import validate_log_format, validate_log_record
from .schema_validators import (
    ValidatorModel,
    create_validator_model,
    validate_json_schema,
    validate_schema,
)
from .timestamp_validators import (
    TIMESTAMP_FORMATS,
    parse_timestamp,
    validate_timestamp,
    validate_timestamp_range,
)
from .url_validators import (
    DOMAIN_PATTERN,
    URL_PATTERN,
    validate_http_url,
    validate_https_url,
    validate_url,
    validate_url_endpoint,
)

__all__ = [
    # Base
    "validate_with",
    "validate_arguments",
    "validate_all",
    "validate_any",
    "get_validation_errors",
    # IP
    "validate_ip_address",
    "validate_ipv4",
    "validate_ipv6",
    "is_private_ip",
    "is_public_ip",
    "IPV4_PATTERN",
    "IPV6_PATTERN",
    # URL
    "validate_url",
    "validate_http_url",
    "validate_https_url",
    "validate_url_endpoint",
    "URL_PATTERN",
    "DOMAIN_PATTERN",
    # HTTP
    "validate_http_method",
    "validate_http_status",
    "validate_http_status_category",
    "get_http_status_category",
    "VALID_HTTP_METHODS",
    "HTTP_STATUS_CATEGORIES",
    # Timestamp
    "validate_timestamp",
    "parse_timestamp",
    "validate_timestamp_range",
    "TIMESTAMP_FORMATS",
    # Schema
    "validate_schema",
    "validate_json_schema",
    "create_validator_model",
    "ValidatorModel",
    # Log
    "validate_log_format",
    "validate_log_record",
    # Config
    "validate_config_dict",
    "validate_env_vars",
    "validate_database_config",
    "validate_full_config",
    "validate_file_paths_config",
    "validate_logging_config",
    "validate_metrics_config",
    "validate_processing_config",
    "_get_nested_value"
    # Composite
    "LogRecordValidator",
    "ConfigValidator",
    "NetworkValidator",
]
