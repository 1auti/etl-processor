"""
Core package for the ETL system.

This module centralizes exports from all core subpackages:
- Configuration system
- Exception hierarchy
- Structured logging
- Utilities and helpers
"""

# Import from config subpackage
from .config import Config, get_config

# Import all exceptions from exceptions subpackage
from .exceptions import (  # Base exception; Checkpoint exceptions; Config exceptions; Enrichment exceptions; File exceptions; Parsing exceptions; Processing exceptions; Retry exceptions; Storage exceptions; Utility exceptions; Validation exceptions
    BatchProcessingError,
    CheckpointCorruptedError,
    CheckpointError,
    CheckpointNotFoundError,
    ConfigurationError,
    DatabaseConnectionError,
    DatabaseInsertError,
    DatabaseQueryError,
    EnrichmentError,
    EtlException,
    FileAlredyProcessedError,
    FileCorruptedError,
    FileError,
    FilePermissionError,
    GeoIpLookupError,
    InvalidConfigError,
    InvalidHttpMethodError,
    InvalidIpAddresError,
    InvalidLogFormatError,
    InvalidStatusCodeError,
    InvalidTimestampError,
    MissingConfigError,
    ParsingError,
    PipelineError,
    ProcessingError,
    RetryExhaustedError,
    StorageError,
    SuspiciousPatternError,
    TransactionError,
    UnsupportedLogFormatError,
    UserAgentParseError,
    ValidationError,
    invalidUrlError,
    utility_error,
)

# Import from logger subpackage
from .logger import (
    MetricsLogger,
    add_caller_info,
    add_log_level,
    add_timestamp,
    configure_logging,
    get_logger,
    log_context,
    log_function_call,
)

# Re-export everything in a clean __all__
__all__ = [
    # Configuration
    "Config",
    "get_config",
    # Logging
    "configure_logging",
    "get_logger",
    "log_function_call",
    "log_context",
    "MetricsLogger",
    "add_caller_info",
    "add_log_level",
    "add_timestamp",
    # Base exception
    "EtlException",
    # All other exceptions
    "CheckpointCorruptedError",
    "CheckpointError",
    "CheckpointNotFoundError",
    "ConfigurationError",
    "InvalidConfigError",
    "MissingConfigError",
    "EnrichmentError",
    "GeoIpLookupError",
    "UserAgentParseError",
    "FileAlredyProcessedError",
    "FileCorruptedError",
    "FileError",
    "FilePermissionError",
    "InvalidLogFormatError",
    "ParsingError",
    "UnsupportedLogFormatError",
    "BatchProcessingError",
    "PipelineError",
    "ProcessingError",
    "RetryExhaustedError",
    "DatabaseConnectionError",
    "DatabaseInsertError",
    "DatabaseQueryError",
    "StorageError",
    "TransactionError",
    "utility_error",
    "InvalidHttpMethodError",
    "InvalidIpAddresError",
    "InvalidStatusCodeError",
    "InvalidTimestampError",
    "invalidUrlError",
    "SuspiciousPatternError",
    "ValidationError",
]

# Package metadata
__version__ = "1.0.0"
__author__ = "ETL System Team"
__description__ = "Core components for the ETL pipeline system"
__email__ = "team@etl-system.com"


# Helper function for initialization
def initialize_core(log_level: str = "INFO", env: str = None):
    """
    Initialize all core components.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        env: Environment for configuration (dev, test, prod)

    Returns:
        Config: Configuration instance
    """
    # Configure logging
    configure_logging(log_level=log_level)

    # Get logger for core initialization
    logger = get_logger(__name__)
    logger.info("Core initialized", log_level=log_level, env=env or "default")

    # Get configuration
    config = get_config(env=env)

    logger.info("Configuration loaded", environment=config.env, config_dir=str(config.config_dir))

    return config
