"""
Abstractions package for the ETL system.

Provides abstract base classes and type definitions that define
the contracts for all ETL components.
"""

# Import from types
from .types import (
    LogRecord,
    LogRecordBatch,
    DBConfig,
    ProcessStats,
    OperationResult,
    ProcessingStatus,
    ProcessingResult,
    ParserStats,
    ExtractionResult
)

# Import from parsers
from .parsers import BaseParser

# Import from processors
from .processors import BaseETLProcessor

# Import from loaders
from .loaders import BaseLoader

# Try to import optional modules (they might not exist yet)
try:
    from .extractors import BaseExtractor
    HAS_EXTRACTORS = True
except ImportError:
    HAS_EXTRACTORS = False
    BaseExtractor = None

try:
    from .loaders import BaseLoader
    HAS_LOADERS = True
except ImportError:
    HAS_LOADERS = False
    BaseLoader = None

# Re-export everything
__all__ = [
    # Types
    'LogRecord',
    'LogRecordBatch',
    'DBConfig',
    'ProcessStats',
    'OperationResult',
    'ProcessingStatus',
    'ProcessingResult',
    'ParserStats',
    'ExtractionResult',

    # Abstract classes
    'BaseParser',
    'BaseETLProcessor',
    'BaseExtractor',
    'BaseLoader',
]

# Version
__version__ = '1.0.0'
__author__ = 'ETL System'
