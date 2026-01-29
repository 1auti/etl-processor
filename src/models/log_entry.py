"""
Modelo LogEntry con validación Pydantic.
Representa una entrada de log web validada (Apache/Nginx).

Integración con abstractions:
- Compatible con LogRecord type alias (Dict[str, Any])
- Puede usarse con BaseParser.parse_line()
- Compatible con LogRecordBatch (List[LogRecord])
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import Field, field_validator, model_validator

from src.core.validators import validate_http_method, validate_http_status, validate_ip_address
from src.models.base import BaseETLModel


class HTTPMethod(str, Enum):
    """Métodos HTTP válidos."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
    CONNECT = "CONNECT"
    TRACE = "TRACE"


class LogEntry(BaseETLModel):
    """
    Entrada de log web validada con Pydantic.

    Uso típico:
    1. Parser genera LogRecord (dict sin validación)
    2. Validar: log = LogEntry.from_log_record(raw_record)
    3. Usar: validated_record = log.to_log_record()

    Compatible con:
    - LogRecord type alias de abstractions
    - BaseParser.parse_line() return
    - LogRecordBatch (List[LogRecord])

    Example:
        >>> # Desde parser (dict sin validación)
        >>> raw: LogRecord = {
        ...     'ip_address': '192.168.1.1',
        ...     'timestamp': datetime.now(),
        ...     'method': 'GET',
        ...     'endpoint': '/api/users',
        ...     'status_code': 200,
        ...     'response_size': 1234,
        ...     'http_version': 'HTTP/1.1'
        ... }
        >>>
        >>> # Validar con Pydantic
        >>> log = LogEntry.from_log_record(raw)
        >>>
        >>> # Propiedades
        >>> log.is_success  # True
        >>> log.is_error    # False
        >>>
        >>> # Convertir de vuelta
        >>> validated_record: LogRecord = log.to_log_record()
    """

    # ========== CAMPOS OBLIGATORIOS ==========
    ip_address: str = Field(
        ...,
        description="Dirección IP del cliente",
        examples=["192.168.1.1", "10.0.0.1", "2001:0db8::1"],
    )

    timestamp: datetime = Field(..., description="Timestamp de la petición")

    method: str = Field(
        ..., description="Método HTTP de la petición", examples=["GET", "POST", "PUT", "DELETE"]
    )

    endpoint: str = Field(..., description="Endpoint/URL solicitado", min_length=1, max_length=2000)

    status_code: int = Field(..., description="Código HTTP de respuesta", ge=100, le=599)

    response_size: int = Field(..., description="Tamaño de la respuesta en bytes", ge=0)

    http_version: str = Field(
        default="HTTP/1.1",
        description="Versión del protocolo HTTP",
        pattern=r"^HTTP/[0-9]\.[0-9]$",
        examples=["HTTP/1.0", "HTTP/1.1", "HTTP/2.0"],
    )

    # ========== CAMPOS OPCIONALES ==========
    user_agent: Optional[str] = Field(None, description="User-Agent del cliente", max_length=1000)

    referer: Optional[str] = Field(None, description="Referer de la petición", max_length=2000)

    remote_user: Optional[str] = Field(
        None, description="Usuario autenticado (si existe)", max_length=255
    )

    request_time: Optional[float] = Field(
        None, description="Tiempo de procesamiento en segundos", ge=0
    )

    # ========== METADATA ==========
    raw_line: Optional[str] = Field(None, description="Línea de log original sin procesar")

    source_file: Optional[str] = Field(None, description="Archivo de origen del log")

    line_number: Optional[int] = Field(
        None, description="Número de línea en el archivo original", ge=1
    )

    # ========== VALIDADORES ==========
    @field_validator("ip_address")
    @classmethod
    def validate_ip(cls, v: str) -> str:
        """Valida dirección IP usando validators del core."""
        if not validate_ip_address(v):
            raise ValueError(f"Dirección IP inválida: {v}")
        return v

    @field_validator("method")
    @classmethod
    def validate_method(cls, v: str) -> str:
        """Valida y normaliza método HTTP."""
        v_upper = v.upper().strip()
        if not validate_http_method(v_upper):
            raise ValueError(f"Método HTTP inválido: {v}")
        return v_upper

    @field_validator("status_code")
    @classmethod
    def validate_status(cls, v: int) -> int:
        """Valida código de estado HTTP."""
        if not validate_http_status(v):
            raise ValueError(f"Código de estado HTTP inválido: {v}")
        return v

    @field_validator("endpoint")
    @classmethod
    def validate_endpoint(cls, v: str) -> str:
        """Valida y sanitiza endpoint."""
        v = v.strip()

        if not v.startswith("/"):
            raise ValueError(f"Endpoint debe comenzar con /: {v}")

        # Detectar patrones sospechosos (XSS, SQL injection, etc)
        suspicious_patterns = [
            "..",  # Path traversal
            "<script",  # XSS
            "javascript:",  # XSS
            "eval(",  # Code injection
            ";--",  # SQL comment
            "DROP TABLE",  # SQL injection
            "UNION SELECT",  # SQL injection
            "../",  # Path traversal
            "..\\",  # Path traversal (Windows)
        ]

        v_lower = v.lower()
        for pattern in suspicious_patterns:
            if pattern.lower() in v_lower:
                raise ValueError(f"Endpoint contiene patrón sospechoso: {pattern}")

        return v

    @model_validator(mode="after")
    def validate_consistency(self):
        """Validaciones de consistencia entre campos."""
        # Si es error (4xx/5xx) con response_size muy grande, es sospechoso
        if self.status_code >= 400 and self.response_size > 100000:
            # Solo advertencia, no falla
            pass

        # Si request_time es muy alto (>60s), podría ser timeout
        if self.request_time and self.request_time > 60:
            pass

        return self

    # ========== PROPIEDADES ==========
    @property
    def is_error(self) -> bool:
        """True si es error 4xx o 5xx."""
        return self.status_code >= 400

    @property
    def is_server_error(self) -> bool:
        """True si es error de servidor (5xx)."""
        return self.status_code >= 500

    @property
    def is_client_error(self) -> bool:
        """True si es error de cliente (4xx)."""
        return 400 <= self.status_code < 500

    @property
    def is_success(self) -> bool:
        """True si es exitoso (2xx)."""
        return 200 <= self.status_code < 300

    @property
    def is_redirect(self) -> bool:
        """True si es redirección (3xx)."""
        return 300 <= self.status_code < 400

    @property
    def is_informational(self) -> bool:
        """True si es informacional (1xx)."""
        return 100 <= self.status_code < 200

    def get_status_category(self) -> str:
        """
        Retorna la categoría del status code.

        Returns:
            str: 'informational', 'success', 'redirection',
                 'client_error', o 'server_error'
        """
        if self.status_code < 200:
            return "informational"
        elif self.status_code < 300:
            return "success"
        elif self.status_code < 400:
            return "redirection"
        elif self.status_code < 500:
            return "client_error"
        else:
            return "server_error"

    def get_method_category(self) -> str:
        """
        Categoriza el método HTTP.

        Returns:
            str: 'read' (GET, HEAD, OPTIONS) o 'write' (POST, PUT, DELETE, PATCH)
        """
        read_methods = {"GET", "HEAD", "OPTIONS"}
        if self.method in read_methods:
            return "read"
        else:
            return "write"
