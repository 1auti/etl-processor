"""
Parser especializado para logs de Nginx.

Soporta:
- Nginx Combined Log Format (default)
- Nginx formato con variables custom ($request_time, $upstream_response_time)

DIFERENCIAS CON APACHE:
- Nginx usa comillas dobles SIEMPRE en request
- Puede incluir tiempos de respuesta adicionales
- Formato de timestamp puede variar según configuración
"""

import re
from datetime import datetime
from typing import List, Optional

from src.core.abstractions.parsers import BaseParser
from src.core.abstractions.types import LogRecord
from src.core.constants.parsing_constants import ParsingConstants


class NginxParser(BaseParser):
    """
    Parser para logs de Nginx HTTP Server.

    Formato soportado (Nginx Combined):
    IP - user [timestamp] "METHOD /url HTTP/1.1" status bytes "referrer" "user-agent"

    Ejemplo:
    172.16.254.1 - - [29/Jan/2026:08:15:32 +0000] "GET /api/v1/users HTTP/1.1" 200 2341 "-" "curl/7.68.0"

    Diferencias con Apache:
    - Request SIEMPRE entre comillas dobles
    - Puede tener campos adicionales (request_time, upstream_time)
    - User puede ser "-" o un username
    """

    # REGEX PATTERN para Nginx Combined Log Format
    # Explicación línea por línea:
    LOG_PATTERN = re.compile(
        r"(?P<ip>\S+) "  # 1. IP del cliente
        r"- "  # 2. Ident (siempre "-" en Nginx)
        r"(?P<user>\S+) "  # 3. Usuario autenticado (o "-")
        r"\[(?P<timestamp>[^\]]+)\] "  # 4. Timestamp entre corchetes
        r'"(?P<request>[^"]*)" '  # 5. Request completo (puede estar vacío)
        r"(?P<status>\d+) "  # 6. Status HTTP
        r"(?P<bytes>\d+|-) "  # 7. Bytes enviados (puede ser "-")
        r'"(?P<referrer>[^"]*)" '  # 8. Referrer (o "-")
        r'"(?P<user_agent>[^"]*)"'  # 9. User-Agent
        r"(?: (?P<request_time>[\d.]+))?"  # 10. Request time (opcional)
        r"(?: (?P<upstream_time>[\d.]+|-))?"  # 11. Upstream time (opcional)
    )

    @property
    def name(self) -> str:
        return "nginx_parser"

    @property
    def supported_formats(self) -> List[str]:
        return ["nginx_combined", "nginx_default"]

    def parse_line(self, line: str) -> Optional[LogRecord]:
        """
        Parsea una línea de log de Nginx.

        Args:
            line: Línea de log cruda

        Returns:
            LogRecord con campos parseados o None si falla

        Ejemplo:
            >>> parser = NginxParser()
            >>> line = '10.0.0.1 - - [29/Jan/2026:10:30:00 +0000] "POST /login HTTP/1.1" 200 512 "-" "Mozilla/5.0"'
            >>> record = parser.parse_line(line)
            >>> print(record['method'])
            'POST'

        NOTA IMPORTANTE:
        Nginx puede loggear requests malformados (sin HTTP version, sin método).
        Ejemplo: "GET" o incluso "" (string vacío).
        Este parser maneja estos casos devolviendo None.
        """
        # 1. Validar longitud máxima (prevenir ataques)
        if len(line) > ParsingConstants.MAX_LINE_LENGTH:
            return None

        # 2. Aplicar regex
        match = self.LOG_PATTERN.match(line.strip())
        if not match:
            return None

        try:
            # 3. Extraer todos los grupos
            data = match.groupdict()

            # 4. Parsear timestamp (mismo formato que Apache)
            timestamp_str = data["timestamp"]
            timestamp = datetime.strptime(timestamp_str, ParsingConstants.APACHE_TIMESTAMP_FORMAT)

            # 5. Parsear el request (METHOD /url HTTP/version)
            # CUIDADO: Puede ser malformado o vacío
            request = data["request"]
            method, url = self._parse_request(request)

            # Si no se pudo parsear el request, es inválido
            if method is None or url is None:
                return None

            # 6. Parsear bytes (puede ser "-")
            bytes_value = data["bytes"]
            bytes_int = 0 if bytes_value == "-" else int(bytes_value)

            # 7. Parsear campos opcionales (tiempos de respuesta)
            request_time = self._parse_float_or_none(data.get("request_time"))
            upstream_time = self._parse_float_or_none(data.get("upstream_time"))

            # 8. Construir registro estructurado
            record = {
                "ip": data["ip"],
                "user": data["user"],  # Nginx incluye este campo
                "timestamp": timestamp,
                "method": method,
                "url": url,
                "status": int(data["status"]),
                "bytes": bytes_int,
                "referrer": data["referrer"] if data["referrer"] != "-" else None,
                "user_agent": data["user_agent"] if data["user_agent"] != "-" else None,
            }

            # 9. Agregar campos opcionales solo si existen
            if request_time is not None:
                record["request_time"] = request_time

            if upstream_time is not None:
                record["upstream_time"] = upstream_time

            return record

        except (ValueError, KeyError) as e:
            # Error en conversión de tipos o campos faltantes
            return None

    def validate_record(self, record: LogRecord) -> bool:
        """
        Valida que un registro parseado de Nginx sea correcto.

        Verifica:
        - Campos requeridos presentes
        - IP válida (IPv4 o IPv6)
        - Status HTTP válido (100-599)
        - Bytes no negativo
        - Método HTTP conocido
        - URL no vacía

        Args:
            record: Registro parseado a validar

        Returns:
            True si el registro es válido
        """
        # 1. Verificar campos requeridos
        required_fields = ["ip", "timestamp", "method", "url", "status", "bytes"]
        if not all(field in record for field in required_fields):
            return False

        # 2. Validar IP (soporta IPv4 e IPv6)
        ip = record["ip"]
        if not (self._is_valid_ipv4(ip) or self._is_valid_ipv6(ip)):
            return False

        # 3. Validar status HTTP (100-599)
        status = record["status"]
        if not (100 <= status <= 599):
            return False

        # 4. Validar bytes (no negativo)
        if record["bytes"] < 0:
            return False

        # 5. Validar método HTTP conocido
        valid_methods = {
            "GET",
            "POST",
            "PUT",
            "DELETE",
            "HEAD",
            "OPTIONS",
            "PATCH",
            "CONNECT",
            "TRACE",
        }
        if record["method"] not in valid_methods:
            return False

        # 6. Validar URL no vacía
        if not record["url"] or len(record["url"]) == 0:
            return False

        # 7. Validar tiempos de respuesta (si existen)
        if "request_time" in record and record["request_time"] < 0:
            return False

        if "upstream_time" in record and record["upstream_time"] < 0:
            return False

        return True

    @staticmethod
    def _parse_request(request: str) -> tuple[Optional[str], Optional[str]]:
        """
        Parsea el campo request de Nginx en método y URL.

        Nginx puede loggear requests de varias formas:
        - Normal: "GET /api/users HTTP/1.1"
        - Sin version: "POST /login"
        - Malformado: "GET"
        - Vacío: ""

        Args:
            request: String del request completo

        Returns:
            Tupla (method, url) o (None, None) si es inválido

        Ejemplos:
            >>> NginxParser._parse_request("GET /home HTTP/1.1")
            ('GET', '/home')
            >>> NginxParser._parse_request("POST /api/login")
            ('POST', '/api/login')
            >>> NginxParser._parse_request("GET")
            (None, None)
            >>> NginxParser._parse_request("")
            (None, None)
        """
        # Request vacío es inválido
        if not request or request.strip() == "":
            return None, None

        # Separar por espacios
        parts = request.split()

        # Debe tener al menos METHOD y URL (HTTP/version es opcional)
        if len(parts) < 2:
            return None, None

        method = parts[0]
        url = parts[1]

        return method, url

    @staticmethod
    def _parse_float_or_none(value: Optional[str]) -> Optional[float]:
        """
        Convierte un string a float, manejando "-" y valores None.

        Args:
            value: String con número o "-" o None

        Returns:
            Float parseado o None

        Ejemplos:
            >>> NginxParser._parse_float_or_none("0.123")
            0.123
            >>> NginxParser._parse_float_or_none("-")
            None
            >>> NginxParser._parse_float_or_none(None)
            None
        """
        if value is None or value == "-":
            return None

        try:
            return float(value)
        except ValueError:
            return None

    @staticmethod
    def _is_valid_ipv4(ip: str) -> bool:
        """
        Valida formato IPv4 básico.

        Args:
            ip: String con dirección IP

        Returns:
            True si es IPv4 válido

        Ejemplo:
            >>> NginxParser._is_valid_ipv4('192.168.1.1')
            True
            >>> NginxParser._is_valid_ipv4('256.1.1.1')
            False
        """
        parts = ip.split(".")

        if len(parts) != ParsingConstants.IPV4_OCTETS:
            return False

        try:
            for part in parts:
                num = int(part)
                if not (ParsingConstants.IPV4_MIN_VALUE <= num <= ParsingConstants.IPV4_MAX_VALUE):
                    return False
            return True
        except ValueError:
            return False

    @staticmethod
    def _is_valid_ipv6(ip: str) -> bool:
        """
        Validación básica de IPv6.

        NOTA: Esta es una validación SIMPLIFICADA.
        Para producción, considerar usar librería 'ipaddress' de Python.

        Args:
            ip: String con dirección IP

        Returns:
            True si parece IPv6 válido

        Ejemplo:
            >>> NginxParser._is_valid_ipv6('2001:0db8:85a3::8a2e:0370:7334')
            True
            >>> NginxParser._is_valid_ipv6('invalid')
            False
        """
        # Validación básica: debe contener ":" y caracteres hexadecimales
        if ":" not in ip:
            return False

        # No debe tener más de 8 grupos (simplificado)
        groups = ip.split(":")
        if len(groups) > 8:
            return False

        # Cada grupo debe ser hexadecimal válido (excepto grupos vacíos por ::)
        valid_chars = set("0123456789abcdefABCDEF")
        for group in groups:
            if group and not all(c in valid_chars for c in group):
                return False

        return True
