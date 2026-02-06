"""
Parser especializado para logs de Apache (Common y Combined Log Format).

Soporta:
- Apache Common Log Format (CLF)
- Apache Combined Log Format (incluyendo referrer y user-agent)
"""

import re
from datetime import datetime
from typing import List, Optional

from src.core.abstractions.parsers import BaseParser
from src.core.abstractions.types import LogRecord
from src.core.constants.parsing_constants import ParsingConstants


class ApacheParser(BaseParser):
    """
    Parser para logs de Apache HTTP Server.

    Formato soportado:
    IP - - [timestamp] "METHOD /url HTTP/1.1" status bytes "referrer" "user-agent"

    Ejemplo:
    192.168.1.1 - - [10/Jan/2026:14:23:45 +0000] "GET /home HTTP/1.1" 200 4523
    """

    # REGEX PATTERN - Explicado línea por línea
    LOG_PATTERN = re.compile(
        r"(?P<ip>\S+) "  # 1. Dirección IP (sin espacios)
        r"\S+ \S+ "  # 2. Ignorar campos ident y authuser
        r"\[(?P<timestamp>[^\]]+)\] "  # 3. Timestamp entre corchetes
        r'"(?P<method>\S+) '  # 4. Método HTTP (GET, POST, etc)
        r"(?P<url>\S+) "  # 5. URL solicitada
        r'[^"]*" '  # 6. Versión HTTP (ignorada)
        r"(?P<status>\d+) "  # 7. Código de estado (200, 404, etc)
        r"(?P<bytes>-|\d+)"  # 8. Bytes (puede ser "-")
        r'(?: "(?P<referrer>[^"]*)" '  # 9. Referrer (opcional)
        r'"(?P<user_agent>[^"]*)")?'  # 10. User-Agent (opcional)
    )

    @property
    def name(self) -> str:
        return "apache_parser"

    @property
    def supported_formats(self) -> List[str]:
        return ["apache_common", "apache_combined"]

    def parse_line(self, line: str) -> Optional[LogRecord]:
        """
        Parsea una línea de log de Apache.

        Args:
            line: Línea de log cruda (debe terminar sin \n)

        Returns:
            LogRecord con campos parseados o None si falla

        Ejemplo:
            >>> parser = ApacheParser()
            >>> line = '192.168.1.1 - - [10/Jan/2026:14:23:45 +0000] "GET /api HTTP/1.1" 200 1234'
            >>> record = parser.parse_line(line)
            >>> print(record['ip'])
            '192.168.1.1'
        """
        # 1. Validar longitud de línea (evitar ataques de memoria)
        if len(line) > ParsingConstants.MAX_LINE_LENGTH:
            return None

        # 2. Aplicar regex
        match = self.LOG_PATTERN.fullmatch(line.strip())
        if not match:
            return None

        try:
            # 3. Extraer grupos nombrados del regex
            data = match.groupdict()

            # 4. Parsear timestamp (formato Apache)
            timestamp_str = data["timestamp"]
            timestamp = datetime.strptime(timestamp_str, ParsingConstants.APACHE_TIMESTAMP_FORMAT)

            # 5. Manejar bytes (puede ser "-" en logs)
            bytes_value = data["bytes"]
            bytes_int = 0 if bytes_value == "-" else int(bytes_value)

            # 6. Construir registro estructurado
            return {
                "ip": data["ip"],
                "timestamp": timestamp,
                "method": data["method"],
                "url": data["url"],
                "status": int(data["status"]),
                "bytes": bytes_int,
                "referrer": data.get("referrer", "-"),
                "user_agent": data.get("user_agent", "-"),
            }

        except (ValueError, KeyError) as e:
            # Error en conversión de tipos o campos faltantes
            # Retornar None, el sistema manejará el error
            return None

    def validate_record(self, record: LogRecord) -> bool:
        """
        Valida que un registro parseado sea correcto.

        Verifica:
        - Campos requeridos presentes
        - IP válida (formato básico)
        - Status HTTP válido (100-599)
        - Bytes no negativo

        Args:
            record: Registro parseado a validar

        Returns:
            True si el registro es válido
        """
        # 1. Verificar campos requeridos
        required_fields = ["ip", "timestamp", "method", "url", "status", "bytes"]
        if not all(field in record for field in required_fields):
            return False

        # 2. Validar IP (formato básico IPv4)
        ip = record["ip"]
        if not self._is_valid_ipv4(ip):
            return False

        # 3. Validar status HTTP (100-599)
        status = record["status"]
        if not (100 <= status <= 599):
            return False

        # 4. Validar bytes (no negativo)
        if record["bytes"] < 0:
            return False

        return True

    @staticmethod
    def _is_valid_ipv4(ip: str) -> bool:
        """
        Valida formato IPv4 básico.

        Args:
            ip: String con dirección IP

        Returns:
            True si es IPv4 válido

        Ejemplo:
            >>> ApacheParser._is_valid_ipv4('192.168.1.1')
            True
            >>> ApacheParser._is_valid_ipv4('999.999.999.999')
            False
        """
        parts = ip.split(".")

        # Debe tener exactamente 4 octetos
        if len(parts) != ParsingConstants.IPV4_OCTETS:
            return False

        try:
            # Cada octeto debe ser 0-255
            for part in parts:
                num = int(part)
                if not (ParsingConstants.IPV4_MIN_VALUE <= num <= ParsingConstants.IPV4_MAX_VALUE):
                    return False
            return True
        except ValueError:
            return False
