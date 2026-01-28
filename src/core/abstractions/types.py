"""
Clase que reprensenta las definiciones base del procesamiento
Contiene:
- definiciones de types
- enums
- dataclases para procesamiento del ETl
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

# ========== TYPE ALIASES ==========
LogRecord = Dict[str, Any]
LogRecordBatch = List[LogRecord]
DBConfig = Dict[str, Any]
ProcessStats = Dict[str, Any]
OperationResult = Tuple[bool, Optional[str]]


# ========== ENUMS ==========
class ProcessingStatus(Enum):
    """Status of ETL processing."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


# ========== DATA CLASSES ==========
@dataclass
class ProcessingResult:
    """Structured result of ETL processing."""

    success: bool
    records_processed: int
    errors: int
    duration_seconds: float
    status: ProcessingStatus
    message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


@dataclass
class ParserStats:
    """Statistics for parsing operations."""

    total_lines: int = 0
    parsed_successfully: int = 0
    parse_errors: int = 0
    validation_errors: int = 0
    duration_seconds: float = 0.0


@dataclass
class ExtractionResult:
    """Result of data extraction."""

    raw_lines: List[str]
    source_info: Dict[str, Any]
    errors: List[str]
