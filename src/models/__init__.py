"""
Modelos Pydantic del sistema ETL.

Relación con abstractions:
- abstractions/types.py define CONTRATOS (dataclasses simples, type aliases)
- models/ define IMPLEMENTACIONES validadas (Pydantic con validación)

Uso típico:
    # 1. Parser genera LogRecord (dict sin validación)
    raw_record: LogRecord = parser.parse_line(line)

    # 2. Validar con Pydantic
    try:
        validated_log = LogEntry.from_log_record(raw_record)
    except ValidationError as e:
        # Manejar error de validación
        pass

    # 3. Usar en batch (convertir de vuelta a LogRecord)
    batch: LogRecordBatch = [log.to_log_record() for log in validated_logs]

    # 4. Cargar con loader
    loader.load_batch(batch)
"""

# Base models
from .base import BaseETLModel
from .immutable_etl_model import ImmutableETLModel

# Log models
from .log_entry import HTTPMethod, LogEntry

# Result models
from .results import ParserStatsModel, ProcessingResultModel, ValidationErrorModel

__all__ = [
    # Base
    "BaseETLModel",
    "ImmutableETLModel",
    # Log models
    "LogEntry",
    "HTTPMethod",
    # Result models
    "ProcessingResultModel",
    "ParserStatsModel",
    "ValidationErrorModel",
]

__version__ = "1.0.0"
