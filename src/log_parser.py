"""
Parsear de logs de Apache / Nginx
Extraer informacion estructurada de archivos de archivos de logs usando expresiones regulares
"""

import re
from datetime import datetime
from typing import Dict, Optional


class LogParser:
    """
    Parsea linea de log en formato Apache/Nginx


    Formato esperado:
    IP - - [timestamp] "METHOD /url HTTP/1.1" status bytes

    Ejemplo:
    192.168.1.1 - - [10/Jan/2026:14:23:45 +0000] "GET /home HTTP/1.1" 200 4523


    """

    # Patrón regex para Apache Combined Log Format
    LOG_PATTERN = re.compile(
        r"(?P<ip>\S+) "  # Dirección IP
        r"\S+ \S+ "  # Campos ignorados (-, -)
        r"\[(?P<timestamp>[^\]]+)\] "  # Timestamp entre []
        r'"(?P<method>\S+) '  # Método HTTP (GET, POST, etc.)
        r"(?P<url>\S+) "  # URL solicitada
        r'\S+" '  # Versión HTTP (ignorada)
        r"(?P<status>\d+) "  # Código de estado HTTP
        r"(?P<bytes>\d+)"  # Bytes transferidos
    )

    # Formato de timestamp de Apache
    TIMESTAMP_FORMAT = "%d/%b/%Y:%H:%M:%S %z"

    @staticmethod
    def parse_line(line: str) -> Optional[Dict]:
        """
        Parsea una línea de log y retorna un diccionario con los datos.

        Args:
            line (str): Línea de log a parsear

        Returns:
            dict: Diccionario con los campos parseados, o None si el formato es inválido

        Example:
            >>> parser = LogParser()
            >>> line = '192.168.1.1 - - [10/Jan/2026:14:23:45 +0000] "GET /home HTTP/1.1" 200 4523'
            >>> result = parser.parse_line(line)
            >>> print(result['ip'])
            '192.168.1.1'
        """
        # Aplicar regex
        match = LogParser.LOG_PATTERN.match(line)

        if not match:
            return None

        try:
            # Extraer grupos del regex
            data = match.groupdict()

            # Convertir timestamp a objeto datetime
            timestamp_str = data["timestamp"]
            timestamp = datetime.strptime(timestamp_str, LogParser.TIMESTAMP_FORMAT)

            # Construir diccionario de salida
            return {
                "ip": data["ip"],
                "timestamp": timestamp,
                "method": data["method"],
                "url": data["url"],
                "status": int(data["status"]),
                "bytes": int(data["bytes"]),
            }

        except (ValueError, KeyError) as e:
            # Error al parsear timestamp o campos inválidos
            print(f"  Error parseando línea: {e}")
            return None

    @staticmethod
    def validate_ip(ip: str) -> bool:
        """
        Valida que la IP tenga formato correcto (básico).

        Args:
            ip (str): Dirección IP a validar

        Returns:
            bool: True si la IP es válida
        """
        # Validación simple de IPv4
        parts = ip.split(".")
        if len(parts) != 4:
            return False

        try:
            return all(0 <= int(part) <= 255 for part in parts)
        except ValueError:
            return False

    @staticmethod
    def is_error_status(status: int) -> bool:
        """
        Determina si un código de estado HTTP es un error.

        Args:
            status (int): Código de estado HTTP

        Returns:
            bool: True si es error (4xx o 5xx)
        """
        return status >= 400


# Testing directo del módulo
if __name__ == "__main__":
    # Ejemplo de uso
    parser = LogParser()

    # Línea de log de ejemplo
    test_line = '192.168.1.100 - - [10/Jan/2026:14:23:45 +0000] "GET /productos HTTP/1.1" 200 4523'

    result = parser.parse_line(test_line)

    if result:
        print("   Parsing exitoso:")
        print(f"  IP: {result['ip']}")
        print(f"  Timestamp: {result['timestamp']}")
        print(f"  Método: {result['method']}")
        print(f"  URL: {result['url']}")
        print(f"  Status: {result['status']}")
        print(f"  Bytes: {result['bytes']}")
    else:
        print(" Error al parsear la línea")
