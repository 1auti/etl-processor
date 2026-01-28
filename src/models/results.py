"""
Modelos Pydantic para resultados de procesamiento.
Versiones validadas de las dataclasses en abstractions/types.py

Diferencias:
- abstractions/ProcessingResult = dataclass simple
- models/ProcessingResultModel = Pydantic validado

El dataclass es el contrato, Pydantic es la implementación validada.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import Field, field_validator

from src.core.abstractions.types import ProcessingStatus

from .base import BaseETLModel, ImmutableETLModel


class ProcessingResultModel(ImmutableETLModel):
    """
    Resultado de procesamiento ETL validado (inmutable).

    Versión Pydantic de abstractions.types.ProcessingResult
    Añade validación de rangos y consistencia lógica.

    Example:
        >>> result = ProcessingResultModel(
        ...     success=True,
        ...     records_processed=1000,
        ...     errors=5,
        ...     duration_seconds=12.5,
        ...     status=ProcessingStatus.COMPLETED,
        ...     message="Procesamiento exitoso"
        ... )
        >>>
        >>> # Es inmutable
        >>> result.success = False  # Raises ValidationError
    """

    success: bool = Field(..., description="Si el procesamiento fue exitoso")

    records_processed: int = Field(
        ..., ge=0, description="Número de registros procesados exitosamente"
    )

    errors: int = Field(..., ge=0, description="Número de errores encontrados")

    duration_seconds: float = Field(..., ge=0, description="Duración del procesamiento en segundos")

    status: ProcessingStatus = Field(..., description="Estado final del procesamiento")

    message: Optional[str] = Field(
        None, max_length=500, description="Mensaje descriptivo del resultado"
    )

    details: Optional[Dict[str, Any]] = Field(
        None, description="Detalles adicionales del procesamiento"
    )

    @field_validator("status")
    @classmethod
    def validate_status_consistency(cls, v, info):
        """Valida consistencia entre success y status."""
        # Si success=True, status NO debe ser FAILED
        if info.data.get("success") and v == ProcessingStatus.FAILED:
            raise ValueError("Inconsistencia: success=True pero status=FAILED")

        # Si success=False, status NO debe ser COMPLETED
        if not info.data.get("success") and v == ProcessingStatus.COMPLETED:
            raise ValueError("Inconsistencia: success=False pero status=COMPLETED")

        return v

    @property
    def success_rate(self) -> float:
        """Tasa de éxito (0.0 a 1.0)."""
        total = self.records_processed + self.errors
        if total == 0:
            return 0.0
        return self.records_processed / total

    @property
    def error_rate(self) -> float:
        """Tasa de error (0.0 a 1.0)."""
        return 1.0 - self.success_rate

    @property
    def throughput(self) -> float:
        """Registros procesados por segundo."""
        if self.duration_seconds == 0:
            return 0.0
        return self.records_processed / self.duration_seconds

    def to_dataclass(self):
        """
        Convierte a la dataclass ProcessingResult de abstractions.

        Returns:
            ProcessingResult: Dataclass original
        """
        from src.core.abstractions.types import ProcessingResult

        return ProcessingResult(
            success=self.success,
            records_processed=self.records_processed,
            errors=self.errors,
            duration_seconds=self.duration_seconds,
            status=self.status,
            message=self.message,
            details=self.details,
        )


class ParserStatsModel(BaseETLModel):
    """
    Estadísticas de parsing validadas.

    Versión Pydantic de abstractions.types.ParserStats
    """

    total_lines: int = Field(default=0, ge=0)
    parsed_successfully: int = Field(default=0, ge=0)
    parse_errors: int = Field(default=0, ge=0)
    validation_errors: int = Field(default=0, ge=0)
    duration_seconds: float = Field(default=0.0, ge=0)

    @field_validator("parsed_successfully")
    @classmethod
    def validate_parsed_not_exceed_total(cls, v, info):
        """Parsed no puede ser mayor que total."""
        total = info.data.get("total_lines", 0)
        if v > total:
            raise ValueError(
                f"parsed_successfully ({v}) no puede ser mayor que " f"total_lines ({total})"
            )
        return v

    @field_validator("parse_errors")
    @classmethod
    def validate_parse_errors_not_exceed_total(cls, v, info):
        """Parse errors no puede ser mayor que total."""
        total = info.data.get("total_lines", 0)
        if v > total:
            raise ValueError(f"parse_errors ({v}) no puede ser mayor que " f"total_lines ({total})")
        return v

    @property
    def success_rate(self) -> float:
        """Tasa de éxito del parsing."""
        if self.total_lines == 0:
            return 0.0
        return self.parsed_successfully / self.total_lines

    @property
    def error_rate(self) -> float:
        """Tasa de error del parsing."""
        if self.total_lines == 0:
            return 0.0
        total_errors = self.parse_errors + self.validation_errors
        return total_errors / self.total_lines

    @property
    def throughput(self) -> float:
        """Líneas procesadas por segundo."""
        if self.duration_seconds == 0:
            return 0.0
        return self.total_lines / self.duration_seconds

    def to_dataclass(self):
        """Convierte a la dataclass ParserStats de abstractions."""
        from src.core.abstractions.types import ParserStats

        return ParserStats(
            total_lines=self.total_lines,
            parsed_successfully=self.parsed_successfully,
            parse_errors=self.parse_errors,
            validation_errors=self.validation_errors,
            duration_seconds=self.duration_seconds,
        )


class ValidationErrorModel(BaseETLModel):
    """
    Error de validación estructurado.

    Representa un error cuando un registro no pasa la validación.
    """

    field_name: str = Field(..., description="Campo que falló la validación")

    invalid_value: Any = Field(..., description="Valor inválido recibido")

    error_message: str = Field(..., description="Mensaje de error detallado")

    line_number: Optional[int] = Field(
        None, ge=1, description="Número de línea donde ocurrió el error"
    )

    raw_line: Optional[str] = Field(None, description="Línea original sin procesar")

    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp del error")

    def __str__(self) -> str:
        """Representación string del error."""
        if self.line_number:
            return (
                f"Línea {self.line_number}: {self.field_name} = "
                f"{self.invalid_value} - {self.error_message}"
            )
        return f"{self.field_name} = {self.invalid_value} - " f"{self.error_message}"
