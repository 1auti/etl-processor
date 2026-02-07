"""
Tests para EnrichedLogEntry y modelos relacionados.
"""

from datetime import datetime

import pytest

from src.models.enriched_log import (
    EnrichedLogEntry,
    GeoLocationInfo,
    LogEntry,
    SessionInfo,
    ThreatInfo,
    UserAgentInfo,
)


class TestGeoLocationInfo:
    """Tests para GeoLocationInfo."""

    def test_create_valid_geo_info(self):
        """Test creación de info geográfica válida."""
        geo = GeoLocationInfo(
            country_code="AR",
            country_name="Argentina",
            city="Buenos Aires",
            latitude=-34.603722,
            longitude=-58.381592,
        )

        assert geo.country_code == "AR"
        assert geo.city == "Buenos Aires"

    def test_latitude_validation(self):
        """Test validación de latitud."""
        with pytest.raises(ValueError):
            GeoLocationInfo(latitude=100)  # Fuera de rango

    def test_longitude_validation(self):
        """Test validación de longitud."""
        with pytest.raises(ValueError):
            GeoLocationInfo(longitude=200)  # Fuera de rango


class TestUserAgentInfo:
    """Tests para UserAgentInfo."""

    def test_create_desktop_user_agent(self):
        """Test creación de UA de desktop."""
        ua = UserAgentInfo(
            browser="Chrome",
            browser_version="120.0",
            os="Windows",
            os_version="10",
            device_type="desktop",
            is_bot=False,
            is_mobile=False,
        )

        assert ua.browser == "Chrome"
        assert ua.is_mobile is False

    def test_create_mobile_user_agent(self):
        """Test creación de UA móvil."""
        ua = UserAgentInfo(
            browser="Safari",
            os="iOS",
            device_type="mobile",
            device_brand="Apple",
            device_model="iPhone",
            is_mobile=True,
        )

        assert ua.is_mobile is True
        assert ua.device_type == "mobile"

    def test_create_bot_user_agent(self):
        """Test creación de UA de bot."""
        ua = UserAgentInfo(is_bot=True, bot_name="Googlebot", device_type="bot")

        assert ua.is_bot is True
        assert ua.bot_name == "Googlebot"


class TestThreatInfo:
    """Tests para ThreatInfo."""

    def test_create_safe_threat_info(self):
        """Test creación de info sin amenaza."""
        threat = ThreatInfo(is_threat=False, threat_score=0)

        assert threat.is_threat is False

    def test_create_threat_info_with_high_score(self):
        """Test creación con score alto."""
        threat = ThreatInfo(
            is_threat=True, threat_level="high", threat_score=85, categories=["malware", "spam"]
        )

        assert threat.is_threat is True
        assert threat.threat_score == 85
        assert "malware" in threat.categories


class TestEnrichedLogEntry:
    """Tests para EnrichedLogEntry."""

    def test_create_enriched_from_basic_log(self, valid_log_record):
        """Test creación de log enriquecido desde log básico."""
        # Crear log básico
        basic_log = LogEntry.from_log_record(valid_log_record)

        # Enriquecer
        enriched = EnrichedLogEntry(
            **basic_log.model_dump(),
            geo_info=GeoLocationInfo(country_code="AR", city="Buenos Aires")
        )

        assert enriched.ip_address == basic_log.ip_address
        assert enriched.geo_info.country_code == "AR"

    def test_is_from_mobile_property(self, valid_log_record):
        """Test propiedad is_from_mobile."""
        enriched = EnrichedLogEntry(
            **LogEntry.from_log_record(valid_log_record).model_dump(),
            user_agent_info=UserAgentInfo(is_mobile=True, device_type="mobile")
        )

        assert enriched.is_from_mobile is True

    def test_is_from_bot_property(self, valid_log_record):
        """Test propiedad is_from_bot."""
        enriched = EnrichedLogEntry(
            **LogEntry.from_log_record(valid_log_record).model_dump(),
            user_agent_info=UserAgentInfo(is_bot=True, bot_name="Googlebot")
        )

        assert enriched.is_from_bot is True

    def test_is_suspicious_with_threat(self, valid_log_record):
        """Test is_suspicious con amenaza."""
        enriched = EnrichedLogEntry(
            **LogEntry.from_log_record(valid_log_record).model_dump(),
            threat_info=ThreatInfo(is_threat=True, threat_score=90)
        )

        assert enriched.is_suspicious is True

    def test_risk_level_calculation(self, valid_log_record):
        """Test cálculo de risk_level."""
        enriched = EnrichedLogEntry(
            **LogEntry.from_log_record(valid_log_record).model_dump(),
            threat_info=ThreatInfo(threat_score=85)
        )

        assert enriched.risk_level == "critical"

    def test_get_location_string(self, valid_log_record):
        """Test get_location_string."""
        enriched = EnrichedLogEntry(
            **LogEntry.from_log_record(valid_log_record).model_dump(),
            geo_info=GeoLocationInfo(city="Buenos Aires", country_name="Argentina")
        )

        location = enriched.get_location_string()
        assert location == "Buenos Aires, Argentina"

    def test_get_device_string(self, valid_log_record):
        """Test get_device_string."""
        enriched = EnrichedLogEntry(
            **LogEntry.from_log_record(valid_log_record).model_dump(),
            user_agent_info=UserAgentInfo(
                browser="Chrome", browser_version="120.0", os="Windows", os_version="10"
            )
        )

        device = enriched.get_device_string()
        assert "Chrome 120.0" in device
        assert "Windows 10" in device
