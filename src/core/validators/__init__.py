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
    validate_with,
    validate_arguments,
    validate_all,
    validate_any,
    get_validation_errors
)

from .ip_validators import (
    validate_ip_address,
    validate_ipv4,
    validate_ipv6,
    is_private_ip,
    is_public_ip,
    IPV4_PATTERN,
    IPV6_PATTERN
)

from .url_validators import (
    validate_url,
    validate_http_url,
    validate_https_url,
    validate_url_endpoint,
    URL_PATTERN,
    DOMAIN_PATTERN
)

from .http_validators import (
    validate_http_method,
    validate_http_status,
    validate_http_status_category,
    get_http_status_category,
    VALID_HTTP_METHODS,
    HTTP_STATUS_CATEGORIES
)

from .timestamp_validators import (
    validate_timestamp,
    parse_timestamp,
    validate_timestamp_range,
    TIMESTAMP_FORMATS
)

from .schema_validators import (
    validate_schema,
    validate_json_schema,
    create_validator_model,
    ValidatorModel
)

from .log_validators import (
    validate_log_format,
    validate_log_record
)

from .config_validators import (
    validate_config_dict,
    validate_env_vars
)

from .composite_validators import (
    LogRecordValidator,
    ConfigValidator,
    NetworkValidator
)

__all__ = [
    # Base
    'validate_with',
    'validate_arguments',
    'validate_all',
    'validate_any',
    'get_validation_errors',

    # IP
    'validate_ip_address',
    'validate_ipv4',
    'validate_ipv6',
    'is_private_ip',
    'is_public_ip',
    'IPV4_PATTERN',
    'IPV6_PATTERN',

    # URL
    'validate_url',
    'validate_http_url',
    'validate_https_url',
    'validate_url_endpoint',
    'URL_PATTERN',
    'DOMAIN_PATTERN',

    # HTTP
    'validate_http_method',
    'validate_http_status',
    'validate_http_status_category',
    'get_http_status_category',
    'VALID_HTTP_METHODS',
    'HTTP_STATUS_CATEGORIES',

    # Timestamp
    'validate_timestamp',
    'parse_timestamp',
    'validate_timestamp_range',
    'TIMESTAMP_FORMATS',

    # Schema
    'validate_schema',
    'validate_json_schema',
    'create_validator_model',
    'ValidatorModel',

    # Log
    'validate_log_format',
    'validate_log_record',

    # Config
    'validate_config_dict',
    'validate_env_vars',

    # Composite
    'LogRecordValidator',
    'ConfigValidator',
    'NetworkValidator'
]
