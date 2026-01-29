"""
Tests de integración entre modelos y abstractions.
"""

from datetime import datetime

import pytest
from attr import dataclass

from src.core.abstractions.types import (
    LogRecord,
    LogRecordBatch,
    ParserStats,
    ProcessingResult,
    ProcessingStatus,
)
from src.models import LogEntry, ParserStatsModel, ProcessingResultModel


class TestLogRecordCompatibility:
    """Tests de compatibilidad con LogRecord type alias."""

    def test_log_entry_to_log_record_type(self, valid_log_record):
        """Test que LogEntry.to_log_record() retorna LogRecord compatible."""
        log = LogEntry.from_log_record(valid_log_record)
        record: LogRecord = log.to_log_record()

        # Verificar que es un Dict[str, Any]
        assert isinstance(record, dict)
        assert all(isinstance(k, str) for k in record.keys())

    def test_batch_conversion(self, valid_log_record):
        """Test conversión de batch de LogEntry a LogRecordBatch."""
        logs = [
            LogEntry.from_log_record(valid_log_record),
            LogEntry.from_log_record(valid_log_record),
            LogEntry.from_log_record(valid_log_record),
        ]

        # Convertir a LogRecordBatch
        batch: LogRecordBatch = [log.to_log_record() for log in logs]

        assert isinstance(batch, list)
        assert len(batch) == 3
        assert all(isinstance(record, dict) for record in batch)

    def test_parser_workflow_simulation(self, sample_apache_log_lines):
        """Test simulacion de workflow completo de parser"""

        # Simulamos el output de parser ( LogRecords sin validacion)
        raw_records: LogRecordBatch = [
            {
                "ip_address": "192.168.1.1",
                "timestamp": datetime.now(),
                "method": "GET",
                "endpoint": "/api/users",
                "status_code": 200,
                "response_size": 1234,
                "http_version": "HTTP/1.1",
            }
            for _ in range(3)
        ]

        # Validamos con pydantic
        validated_logs = []
        for record in raw_records:
            try:
                log = LogEntry.from_log_record(record)
                validated_logs.append(log)
            except Exception:
                pass
        # Convertir de vuelta a LogRecordBath para loader
        batch_for_loader: LogRecordBatch = [log.to_log_record() for log in validated_logs]

        assert len(batch_for_loader) == 3
        assert all(isinstance(r, dict) for r in batch_for_loader)


class TestProcessingResultDataclassCompatibility:
    """Test de compatibilidad con dataclases de abstracciones"""

    def test_processing_result_to_dataclass(self, processing_result_data):
        """Test de conversion ProcessingResultModel a dataclases."""
        model = ProcessingResultModel(**processing_result_data)
        dataclass_obj = model.to_dataclass()

        # Verificar que es la dataclass correcta
        assert isinstance(dataclass_obj, ProcessingResult)

        # Verificmaos los campos
        assert dataclass_obj.success == model.success
        assert dataclass_obj.records_processed == model.records_processed
        assert dataclass_obj.errors == model.errors
        assert dataclass_obj.duration_seconds == model.duration_seconds
        assert dataclass_obj.status == model.status

    def test_parse_stats_to_dataclass(self):
        """Test conversion ParserStatsMOdel a dataclasss"""
        model = ParserStatsModel(
            total_lines=1000,
            parsed_successfully=950,
            parse_errors=50,
            validation_errors=0,
            duration_seconds=10.0,
        )

        dataclass_obj = model.to_dataclass()

        assert isinstance(dataclass_obj, ParserStats)
        assert dataclass_obj.total_lines == model.total_lines


class TestEndToEndWorkflow:
    """Test de workflow completo end-to-end"""

    def test_complete_etl_workflow(self, valid_log_record):
        """Test workflow ETL completo con modelos."""

        # 1. EXTRACT - Simular líneas extraídas
        raw_lines = ["log line 1", "log line 2", "log line 3"]

        # 2. TRANSFORM - Parser genera LogRecords
        raw_records: LogRecordBatch = [valid_log_record.copy() for _ in raw_lines]

        # 3. VALIDATE - Validar con Pydantic
        validated_logs = []
        parse_errors = 0

        for record in raw_records:
            try:
                log = LogEntry.from_log_record(record)
                validated_logs.append(log)
            except Exception:
                parse_errors += 1

        # 4. LOAD - Convertir a LogRecordBatch para loader
        batch_for_loader: LogRecordBatch = [log.to_log_record() for log in validated_logs]

        # 5. RESULT - Crear resultado de procesamiento
        result = ProcessingResultModel(
            success=True,
            records_processed=len(batch_for_loader),
            errors=parse_errors,
            duration_seconds=5.0,
            status=ProcessingStatus.COMPLETED,
            message="Procesamiento completado",
        )

        # Verificaciones
        assert result.records_processed == 3
        assert result.errors == 0
        assert result.success is True
        assert len(batch_for_loader) == 3
