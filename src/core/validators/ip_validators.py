"""
IP address validators (IPv4, IPv6).
"""

import re
import ipaddress
from typing import Optional

# Patrones regex
IPV4_PATTERN = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
IPV6_PATTERN = r'^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))$'


def validate_ip_address(ip_string: str, version: Optional[int] = None) -> bool:
    """Valida una dirección IP (IPv4 o IPv6)."""
    if not ip_string or not isinstance(ip_string, str):
        return False

    try:
        ip = ipaddress.ip_address(ip_string)

        if version is None:
            return True
        elif version == 4:
            return isinstance(ip, ipaddress.IPv4Address)
        elif version == 6:
            return isinstance(ip, ipaddress.IPv6Address)
        else:
            return False

    except (ValueError, ipaddress.AddressValueError):
        return False


def validate_ipv4(ip_string: str) -> bool:
    """Valida específicamente IPv4."""
    return validate_ip_address(ip_string, version=4)


def validate_ipv6(ip_string: str) -> bool:
    """Valida específicamente IPv6."""
    return validate_ip_address(ip_string, version=6)


def is_private_ip(ip_string: str) -> bool:
    """Verifica si una IP es privada (RFC 1918)."""
    try:
        ip = ipaddress.ip_address(ip_string)
        return ip.is_private
    except (ValueError, ipaddress.AddressValueError):
        return False


def is_public_ip(ip_string: str) -> bool:
    """Verifica si una IP es pública."""
    try:
        ip = ipaddress.ip_address(ip_string)
        return ip.is_global and not ip.is_private
    except (ValueError, ipaddress.AddressValueError):
        return False
