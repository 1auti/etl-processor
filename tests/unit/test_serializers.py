"""
Tests para serialización/deserialización avanzada.
"""

from datetime import datetime

import pytest

from src.models import LogEntry, ModelDeserializer, ModelSerializer


class TestModelSerializer:
    """Tests para ModelSerializer."""

    def test_to_csv_row(self, valid_log_record):
        """Test serialización a CSV row."""
        log = LogEntry.from_log_record(valid_log_record)

        csv_row = ModelSerializer.to_csv_row(log)

        assert isinstance(csv_row, str)
        assert "192.168.1.1" in csv_row
        assert "GET" in csv_row

    def test_to_csv_batch(self, valid_log_record):
        """Test serialización de batch a CSV."""
        logs = [
            LogEntry.from_log_record(valid_log_record),
            LogEntry.from_log_record(valid_log_record),
        ]

        csv_data = ModelSerializer.to_csv_batch(logs)

        assert isinstance(csv_data, str)
        assert "ip_address" in csv_data  # Header
        assert csv_data.count("\n") == 3  # Header + 2 rows

    def test_to_yaml(self, valid_log_record):
        """Test serialización a YAML."""
        log = LogEntry.from_log_record(valid_log_record)

        yaml_str = ModelSerializer.to_yaml(log)

        assert isinstance(yaml_str, str)
        assert "ip_address:" in yaml_str
        assert "192.168.1.1" in yaml_str

    def test_to_xml(self, valid_log_record):
        """Test serialización a XML."""
        log = LogEntry.from_log_record(valid_log_record)

        xml_str = ModelSerializer.to_xml(log)

        assert isinstance(xml_str, str)
        assert "<log_entry>" in xml_str
        assert "<ip_address>192.168.1.1</ip_address>" in xml_str

    def test_to_msgpack(self, valid_log_record):
        """Test serialización a MessagePack."""
        log = LogEntry.from_log_record(valid_log_record)

        msgpack_bytes = ModelSerializer.to_msgpack(log)

        assert isinstance(msgpack_bytes, bytes)
        assert len(msgpack_bytes) > 0


class TestRoundTrip:
    """Tests de round-trip (serializar y deserializar)."""

    def test_json_round_trip(self, valid_log_record):
        """Test round-trip con JSON."""
        original = LogEntry.from_log_record(valid_log_record)

        # Serializar
        json_str = original.to_json()

        # Deserializar
        restored = LogEntry.from_json(json_str)

        assert original.ip_address == restored.ip_address
        assert original.method == restored.method
        assert original.status_code == restored.status_code

    def test_dict_round_trip(self, valid_log_record):
        """Test round-trip con Dict."""
        original = LogEntry.from_log_record(valid_log_record)

        # Serializar
        data_dict = original.to_dict()

        # Deserializar
        restored = LogEntry.from_dict(data_dict)

        assert original.ip_address == restored.ip_address
        assert original.endpoint == restored.endpoint
