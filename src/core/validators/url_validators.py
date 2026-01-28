"""
URL and domain validators.
"""

import re
from typing import List
from urllib.parse import urlparse

# Patrones regex
URL_PATTERN = r"^(https?|ftp)://[^\s/$.?#].[^\s]*$"
DOMAIN_PATTERN = r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z0-9-]{1,63}(?<!-))*\.[A-Za-z]{2,}$"


def validate_url(url_string: str, require_https: bool = False) -> bool:
    """Valida una URL."""
    if not url_string or not isinstance(url_string, str):
        return False

    if not re.match(URL_PATTERN, url_string, re.IGNORECASE):
        return False

    try:
        parsed = urlparse(url_string)

        if require_https and parsed.scheme.lower() != "https":
            return False

        if not parsed.netloc:
            return False

        if parsed.scheme in ("http", "https"):
            domain = parsed.netloc.split(":")[0]
            if not re.match(DOMAIN_PATTERN, domain, re.IGNORECASE):
                return False

        return True

    except Exception:
        return False


def validate_http_url(url_string: str) -> bool:
    """Valida URLs HTTP/HTTPS."""
    return validate_url(url_string) and urlparse(url_string).scheme in ("http", "https")


def validate_https_url(url_string: str) -> bool:
    """Valida URLs HTTPS exclusivamente."""
    return validate_url(url_string, require_https=True)


def validate_url_endpoint(url_string: str, allowed_paths: List[str] = None) -> bool:
    """Valida URL y verifica que el endpoint esté permitido."""
    if not validate_url(url_string):
        return False

    if allowed_paths:
        parsed = urlparse(url_string)
        path = parsed.path

        if not any(path.startswith(allowed_path) for allowed_path in allowed_paths):
            return False

    return True
