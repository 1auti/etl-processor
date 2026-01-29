"""
Tests para BaseETLModel.
"""

from datetime import datetime

import pytest
from pydantic import ValidationError

from src.models.base import BaseETLModel
from src.models.immutable_etl_model import ImmutableETLModel


class TestModel(BaseETLModel):
    """Modelo de prueba simple."""

    name: str
    value: int
    timestamp: datetime


class TestBaseETLModel:
    """Tests para BaseETLModel."""

    def test_create_valid_model(self):
        """Test creación de modelo válido."""
        model = TestModel(name="test", value=42, timestamp=datetime.now())

        assert model.name == "test"
        assert model.value == 42
        assert isinstance(model.timestamp, datetime)

    def test_to_log_record_conversion(self):
        """Test conversión a LogRecord (Dict)."""
        model = TestModel(name="test", value=42, timestamp=datetime(2024, 1, 15, 10, 0, 0))

        record = model.to_log_record()

        assert isinstance(record, dict)
        assert record["name"] == "test"
        assert record["value"] == 42
        assert "timestamp" in record

    def test_from_log_record_creation(self):
        """Test creación desde LogRecord."""
        record = {"name": "from_dict", "value": 100, "timestamp": datetime.now()}

        model = TestModel.from_log_record(record)

        assert model.name == "from_dict"
        assert model.value == 100

    def test_to_json_serialization(self):
        """Test serialización a JSON."""
        model = TestModel(name="json_test", value=123, timestamp=datetime(2024, 1, 15, 10, 0, 0))

        json_str = model.to_json()

        assert isinstance(json_str, str)
        assert '"name":"json_test"' in json_str
        assert '"value":123' in json_str

    def test_from_json_deserialization(self):
        """Test deserialización desde JSON."""
        json_str = '{"name":"from_json","value":456,"timestamp":"2024-01-15T10:00:00"}'

        model = TestModel.from_json(json_str)

        assert model.name == "from_json"
        assert model.value == 456

    def test_extra_fields_forbidden(self):
        """Test que campos extra son rechazados."""
        with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
            TestModel(
                name="test",
                value=42,
                timestamp=datetime.now(),
                extra_field="not allowed",  # Campo extra
            )

    def test_strict_type_validation(self):
        """Test validación estricta de tipos."""
        with pytest.raises(ValidationError):
            TestModel(name="test", value="not_an_int", timestamp=datetime.now())  # Debería ser int

    def test_validate_assignment(self):
        """Test que asignaciones post-init son validadas."""
        model = TestModel(name="test", value=42, timestamp=datetime.now())

        with pytest.raises(ValidationError):
            model.value = "invalid"  # Asignación con tipo inválido


class TestImmutableETLModel:
    """Tests para ImmutableETLModel."""

    class ImmutableTest(ImmutableETLModel):
        name: str
        value: int

    def test_immutable_after_creation(self):
        """Test que el modelo es inmutable después de creación."""
        model = self.ImmutableTest(name="test", value=42)

        with pytest.raises(ValidationError, match="Instance is frozen"):
            model.value = 100

    def test_can_read_values(self):
        """Test que se pueden leer valores aunque sea inmutable."""
        model = self.ImmutableTest(name="test", value=42)

        assert model.name == "test"
        assert model.value == 42
