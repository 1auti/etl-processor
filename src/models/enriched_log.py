"""
Modelo de log enriquecido con información adicional.
Extiende LogEntry con datos de geolocalización, user-agent parsing, threat intel, etc.
"""

from typing import Optional

from pydantic import Field, field_validator

from .base import BaseETLModel
from .log_entry import LogEntry


class GeoLocationInfo(BaseETLModel):
    """
    Información de geolocalización de una IP.

    Obtenida típicamente de servicios como MaxMind, IP2Location, etc.
    """

    country_code: Optional[str] = Field(
        None,
        max_length=2,
        description="Código de país ISO 3166-1 alpha-2",
        examples=["US", "AR", "BR"],
    )

    country_name: Optional[str] = Field(
        None,
        max_length=100,
        description="Nombre del país",
        examples=["United States", "Argentina", "Brazil"],
    )

    city: Optional[str] = Field(
        None,
        max_length=100,
        description="Ciudad",
        examples=["New York", "Buenos Aires", "São Paulo"],
    )

    region: Optional[str] = Field(None, max_length=100, description="Región/Estado/Provincia")

    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Latitud geográfica")

    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Longitud geográfica")

    timezone: Optional[str] = Field(
        None,
        max_length=50,
        description="Timezone",
        examples=["America/New_York", "America/Argentina/Buenos_Aires"],
    )

    isp: Optional[str] = Field(None, max_length=200, description="Internet Service Provider")

    organization: Optional[str] = Field(
        None, max_length=200, description="Organización dueña de la IP"
    )

    asn: Optional[int] = Field(None, description="Autonomous System Number")


class UserAgentInfo(BaseETLModel):
    """
    Información parseada del User-Agent.

    Obtenida típicamente de libraries como user-agents, ua-parser, etc.
    """

    browser: Optional[str] = Field(
        None,
        max_length=50,
        description="Navegador",
        examples=["Chrome", "Firefox", "Safari", "Edge"],
    )

    browser_version: Optional[str] = Field(
        None, max_length=20, description="Versión del navegador", examples=["120.0", "119.0.1"]
    )

    os: Optional[str] = Field(
        None,
        max_length=50,
        description="Sistema operativo",
        examples=["Windows", "macOS", "Linux", "Android", "iOS"],
    )

    os_version: Optional[str] = Field(
        None,
        max_length=20,
        description="Versión del sistema operativo",
        examples=["10", "14.2", "Ubuntu 22.04"],
    )

    device_type: Optional[str] = Field(
        None,
        max_length=20,
        description="Tipo de dispositivo",
        examples=["desktop", "mobile", "tablet", "bot"],
    )

    device_brand: Optional[str] = Field(
        None,
        max_length=50,
        description="Marca del dispositivo",
        examples=["Apple", "Samsung", "Google"],
    )

    device_model: Optional[str] = Field(
        None,
        max_length=50,
        description="Modelo del dispositivo",
        examples=["iPhone", "Galaxy S23", "Pixel 8"],
    )

    is_bot: bool = Field(default=False, description="Si es un bot/crawler")

    bot_name: Optional[str] = Field(
        None,
        max_length=50,
        description="Nombre del bot si es bot",
        examples=["Googlebot", "Bingbot", "Slackbot"],
    )

    is_mobile: bool = Field(default=False, description="Si es dispositivo móvil")

    is_tablet: bool = Field(default=False, description="Si es tablet")


class ThreatInfo(BaseETLModel):
    """
    Información de threat intelligence.

    Obtenida de servicios como AbuseIPDB, VirusTotal, etc.
    """

    is_threat: bool = Field(default=False, description="Si la IP es considerada amenaza")

    threat_level: Optional[str] = Field(
        None,
        max_length=20,
        description="Nivel de amenaza",
        examples=["low", "medium", "high", "critical"],
    )

    threat_score: Optional[int] = Field(None, ge=0, le=100, description="Score de amenaza (0-100)")

    is_vpn: bool = Field(default=False, description="Si la IP es de VPN")

    is_proxy: bool = Field(default=False, description="Si la IP es de proxy")

    is_tor: bool = Field(default=False, description="Si la IP es de red Tor")

    is_datacenter: bool = Field(default=False, description="Si la IP es de datacenter")

    abuse_confidence_score: Optional[int] = Field(
        None, ge=0, le=100, description="Score de confianza de abuso (AbuseIPDB)"
    )

    categories: Optional[list[str]] = Field(
        None, description="Categorías de amenaza", examples=[["malware", "spam"], ["brute-force"]]
    )

    last_seen_at: Optional[str] = Field(None, description="Última vez vista en actividad maliciosa")


class SessionInfo(BaseETLModel):
    """
    Información de sesión del usuario.

    Calculada a partir de múltiples peticiones del mismo usuario.
    """

    session_id: Optional[str] = Field(None, max_length=64, description="ID de sesión calculado")

    is_new_session: bool = Field(default=True, description="Si es sesión nueva")

    session_duration_seconds: Optional[float] = Field(
        None, ge=0, description="Duración de la sesión en segundos"
    )

    pages_visited: Optional[int] = Field(None, ge=0, description="Páginas visitadas en la sesión")

    referrer_domain: Optional[str] = Field(
        None, max_length=200, description="Dominio de referencia"
    )


class EnrichedLogEntry(LogEntry):
    """
    Entrada de log enriquecida con información adicional.

    Extiende LogEntry añadiendo:
    - Geolocalización de IP
    - Información de User-Agent parseada
    - Threat intelligence
    - Información de sesión

    Este modelo se usa DESPUÉS del procesamiento básico,
    cuando se enriquecen los logs con datos externos.

    Example:
        >>> # 1. Parsear log básico
        >>> basic_log = LogEntry.from_log_record(raw_record)
        >>>
        >>> # 2. Enriquecer con geo, user-agent, etc
        >>> enriched = EnrichedLogEntry(
        ...     **basic_log.model_dump(),
        ...     geo_info=GeoLocationInfo(
        ...         country_code="AR",
        ...         city="Buenos Aires"
        ...     ),
        ...     user_agent_info=UserAgentInfo(
        ...         browser="Chrome",
        ...         os="Windows",
        ...         device_type="desktop"
        ...     )
        ... )
    """

    # ========== INFORMACIÓN ENRIQUECIDA ==========

    geo_info: Optional[GeoLocationInfo] = Field(
        None, description="Información de geolocalización de la IP"
    )

    user_agent_info: Optional[UserAgentInfo] = Field(
        None, description="Información parseada del User-Agent"
    )

    threat_info: Optional[ThreatInfo] = Field(
        None, description="Información de threat intelligence"
    )

    session_info: Optional[SessionInfo] = Field(
        None, description="Información de sesión del usuario"
    )

    # ========== METADATA DE ENRIQUECIMIENTO ==========

    enrichment_timestamp: Optional[str] = Field(
        None, description="Timestamp cuando se enriqueció el log"
    )

    enrichment_sources: Optional[list[str]] = Field(
        None,
        description="Fuentes usadas para enriquecimiento",
        examples=[["maxmind_geoip", "abuseipdb", "user_agents"]],
    )

    # ========== PROPIEDADES DERIVADAS ==========

    @property
    def is_from_mobile(self) -> bool:
        """True si la petición viene de dispositivo móvil."""
        if self.user_agent_info:
            return self.user_agent_info.is_mobile
        return False

    @property
    def is_from_bot(self) -> bool:
        """True si la petición viene de un bot."""
        if self.user_agent_info:
            return self.user_agent_info.is_bot
        return False

    @property
    def is_suspicious(self) -> bool:
        """
        True si la petición es sospechosa.

        Considera:
        - Threat score alto
        - VPN/Proxy/Tor
        - Status code de error con patrones sospechosos
        """
        if self.threat_info:
            if self.threat_info.is_threat:
                return True
            if self.threat_info.threat_score and self.threat_info.threat_score > 70:
                return True
            if self.threat_info.is_tor or self.threat_info.is_proxy:
                return True

        # Error 4xx/5xx con endpoint sospechoso
        if self.is_error and any(
            pattern in self.endpoint.lower() for pattern in ["..", "admin", "config", "backup"]
        ):
            return True

        return False

    @property
    def risk_level(self) -> str:
        """
        Nivel de riesgo de la petición.

        Returns:
            str: 'low', 'medium', 'high', 'critical'
        """
        if not self.threat_info:
            return "low"

        if self.threat_info.threat_level:
            return self.threat_info.threat_level

        # Calcular basado en score
        if self.threat_info.threat_score:
            score = self.threat_info.threat_score
            if score >= 80:
                return "critical"
            elif score >= 60:
                return "high"
            elif score >= 30:
                return "medium"

        return "low"

    def get_location_string(self) -> Optional[str]:
        """
        Retorna ubicación como string legible.

        Returns:
            str: "City, Country" o None
        """
        if not self.geo_info:
            return None

        parts = []
        if self.geo_info.city:
            parts.append(self.geo_info.city)
        if self.geo_info.country_name:
            parts.append(self.geo_info.country_name)

        return ", ".join(parts) if parts else None

    def get_device_string(self) -> Optional[str]:
        """
        Retorna información del dispositivo como string.

        Returns:
            str: "Chrome 120.0 on Windows 10" o None
        """
        if not self.user_agent_info:
            return None

        parts = []

        if self.user_agent_info.browser:
            browser = self.user_agent_info.browser
            if self.user_agent_info.browser_version:
                browser += f" {self.user_agent_info.browser_version}"
            parts.append(browser)

        if self.user_agent_info.os:
            os_str = self.user_agent_info.os
            if self.user_agent_info.os_version:
                os_str += f" {self.user_agent_info.os_version}"
            parts.append(f"on {os_str}")

        return " ".join(parts) if parts else None
