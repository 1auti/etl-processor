"""
Tests para modelos de resultados.
"""

import pytest
from pydantic import ValidationError

from src.core.abstractions.types import ProcessingStatus
from src.models import ParserStatsModel, ProcessingResultModel, ValidationErrorModel


class TestProcessingResultModel:
    """Tests para ProcessingResultModel."""

    def test_create_valid_result(self, processing_result_data):
        """Test creación de resultado válido."""
        result = ProcessingResultModel(**processing_result_data)

        assert result.success is True
        assert result.records_processed == 1000
        assert result.errors == 5
        assert result.duration_seconds == 12.5
        assert result.status == ProcessingStatus.COMPLETED

    def test_status_consistency_validation_success_completed(self):
        """Test consistencia: success=True con COMPLETED."""
        result = ProcessingResultModel(
            success=True,
            records_processed=100,
            errors=0,
            duration_seconds=5.0,
            status=ProcessingStatus.COMPLETED,
        )

        assert result.success is True
        assert result.status == ProcessingStatus.COMPLETED

    def test_status_consistency_validation_fail_failed(self):
        """Test consistencia: success=False con FAILED."""
        result = ProcessingResultModel(
            success=False,
            records_processed=0,
            errors=10,
            duration_seconds=5.0,
            status=ProcessingStatus.FAILED,
        )

        assert result.success is False
        assert result.status == ProcessingStatus.FAILED

    def test_inconsistent_success_true_status_failed_raises_error(self):
        """Test que success=True con FAILED levanta error."""
        with pytest.raises(ValidationError, match="Inconsistencia"):
            ProcessingResultModel(
                success=True,
                records_processed=100,
                errors=0,
                duration_seconds=5.0,
                status=ProcessingStatus.FAILED,  # Inconsistente
            )

    def test_inconsistent_success_false_status_completed_raises_error(self):
        """Test que success=False con COMPLETED levanta error."""
        with pytest.raises(ValidationError, match="Inconsistencia"):
            ProcessingResultModel(
                success=False,
                records_processed=0,
                errors=10,
                duration_seconds=5.0,
                status=ProcessingStatus.COMPLETED,  # Inconsistente
            )

    def test_success_rate_calculation(self):
        """Test cálculo de success_rate."""
        result = ProcessingResultModel(
            success=True,
            records_processed=90,
            errors=10,
            duration_seconds=10.0,
            status=ProcessingStatus.COMPLETED,
        )

        assert result.success_rate == 0.9  # 90/100

    def test_error_rate_calculation(self):
        """Test cálculo de error_rate."""
        result = ProcessingResultModel(
            success=True,
            records_processed=80,
            errors=20,
            duration_seconds=10.0,
            status=ProcessingStatus.COMPLETED,
        )

        assert result.error_rate == pytest.approx(0.2)  # 20/100

    def test_throughput_calculation(self):
        """Test cálculo de throughput."""
        result = ProcessingResultModel(
            success=True,
            records_processed=1000,
            errors=0,
            duration_seconds=10.0,
            status=ProcessingStatus.COMPLETED,
        )

        assert result.throughput == 100.0  # 1000/10

    def test_model_is_immutable(self, processing_result_data):
        """Test que el modelo es inmutable."""
        result = ProcessingResultModel(**processing_result_data)

        with pytest.raises(ValidationError, match="frozen"):
            result.success = False

    def test_to_dataclass_conversion(self, processing_result_data):
        """Test conversión a dataclass."""
        model = ProcessingResultModel(**processing_result_data)
        dataclass_obj = model.to_dataclass()

        from src.core.abstractions.types import ProcessingResult

        assert isinstance(dataclass_obj, ProcessingResult)
        assert dataclass_obj.success == model.success
        assert dataclass_obj.records_processed == model.records_processed


class TestParserStatsModel:
    """Tests para ParserStatsModel."""

    def test_create_valid_stats(self):
        """Test creación de stats válidas."""
        stats = ParserStatsModel(
            total_lines=1000,
            parsed_successfully=950,
            parse_errors=30,
            validation_errors=20,
            duration_seconds=5.5,
        )

        assert stats.total_lines == 1000
        assert stats.parsed_successfully == 950
        assert stats.parse_errors == 30

    def test_parsed_cannot_exceed_total(self):
        """Test que parsed no puede ser mayor que total."""
        with pytest.raises(ValidationError, match="no puede ser mayor"):
            ParserStatsModel(
                total_lines=100,
                parsed_successfully=150,  # Mayor que total
                parse_errors=0,
                validation_errors=0,
            )

    def test_parse_errors_cannot_exceed_total(self):
        """Test que parse_errors no puede ser mayor que total."""
        with pytest.raises(ValidationError, match="no puede ser mayor"):
            ParserStatsModel(
                total_lines=100,
                parsed_successfully=50,
                parse_errors=150,  # Mayor que total
                validation_errors=0,
            )

    def test_success_rate_calculation(self):
        """Test cálculo de success_rate."""
        stats = ParserStatsModel(
            total_lines=100, parsed_successfully=80, parse_errors=20, validation_errors=0
        )

        assert stats.success_rate == 0.8

    def test_error_rate_calculation(self):
        """Test cálculo de error_rate."""
        stats = ParserStatsModel(
            total_lines=100, parsed_successfully=70, parse_errors=20, validation_errors=10
        )

        # error_rate = (parse_errors + validation_errors) / total
        assert stats.error_rate == 0.3  # 30/100

    def test_throughput_calculation(self):
        """Test cálculo de throughput."""
        stats = ParserStatsModel(
            total_lines=1000,
            parsed_successfully=900,
            parse_errors=100,
            validation_errors=0,
            duration_seconds=10.0,
        )

        assert stats.throughput == 100.0  # 1000/10

    def test_to_dataclass_conversion(self):
        """Test conversión a dataclass."""
        model = ParserStatsModel(
            total_lines=100,
            parsed_successfully=90,
            parse_errors=10,
            validation_errors=0,
            duration_seconds=5.0,
        )

        dataclass_obj = model.to_dataclass()

        from src.core.abstractions.types import ParserStats

        assert isinstance(dataclass_obj, ParserStats)
        assert dataclass_obj.total_lines == model.total_lines


class TestValidationErrorModel:
    """Tests para ValidationErrorModel."""

    def test_create_validation_error(self):
        """Test creación de error de validación."""
        error = ValidationErrorModel(
            field_name="ip_address",
            invalid_value="999.999.999.999",
            error_message="Dirección IP inválida",
        )

        assert error.field_name == "ip_address"
        assert error.invalid_value == "999.999.999.999"
        assert error.error_message == "Dirección IP inválida"

    def test_create_with_line_number(self):
        """Test creación con número de línea."""
        error = ValidationErrorModel(
            field_name="status_code",
            invalid_value=999,
            error_message="Status code inválido",
            line_number=42,
            raw_line='192.168.1.1 - - [15/Jan/2024] "GET / HTTP/1.1" 999 100',
        )

        assert error.line_number == 42
        assert error.raw_line is not None

    def test_str_representation_with_line_number(self):
        """Test representación string con número de línea."""
        error = ValidationErrorModel(
            field_name="method",
            invalid_value="INVALID",
            error_message="Método HTTP inválido",
            line_number=10,
        )

        error_str = str(error)

        assert "Línea 10" in error_str
        assert "method" in error_str
        assert "INVALID" in error_str

    def test_str_representation_without_line_number(self):
        """Test representación string sin número de línea."""
        error = ValidationErrorModel(
            field_name="endpoint",
            invalid_value="/test/../../../etc/passwd",
            error_message="Endpoint contiene patrón sospechoso",
        )

        error_str = str(error)

        assert "endpoint" in error_str
        assert "sospechoso" in error_str
        assert "Línea" not in error_str

    def test_timestamp_auto_generated(self):
        """Test que timestamp se genera automáticamente."""
        error = ValidationErrorModel(
            field_name="test", invalid_value="value", error_message="error"
        )

        assert error.timestamp is not None
        from datetime import datetime

        assert isinstance(error.timestamp, datetime)
