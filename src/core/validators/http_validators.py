"""
HTTP protocol validators.
"""

from typing import Optional, Union

# Métodos HTTP válidos
VALID_HTTP_METHODS = {
    "GET",
    "POST",
    "PUT",
    "DELETE",
    "HEAD",
    "OPTIONS",
    "PATCH",
    "TRACE",
    "CONNECT",
}

# Códigos de estado HTTP por categoría
HTTP_STATUS_CATEGORIES = {
    "informational": range(100, 200),
    "success": range(200, 300),
    "redirection": range(300, 400),
    "client_error": range(400, 500),
    "server_error": range(500, 600),
}


def validate_http_method(method: str) -> bool:
    """Valida un método HTTP."""
    if not method or not isinstance(method, str):
        return False

    return method.upper() in VALID_HTTP_METHODS


def validate_http_status(status_code: Union[int, str]) -> bool:
    """Valida un código de estado HTTP."""
    try:
        code = int(status_code)
        return 100 <= code <= 599
    except (ValueError, TypeError):
        return False


def validate_http_status_category(status_code: Union[int, str], category: str) -> bool:
    """Valida que un código de estado pertenezca a una categoría específica."""
    if category not in HTTP_STATUS_CATEGORIES:
        return False

    try:
        code = int(status_code)
        return code in HTTP_STATUS_CATEGORIES[category]
    except (ValueError, TypeError):
        return False


def get_http_status_category(status_code: Union[int, str]) -> Optional[str]:
    """Obtiene la categoría de un código de estado HTTP."""
    if not validate_http_status(status_code):
        return None

    try:
        code = int(status_code)
        for category, code_range in HTTP_STATUS_CATEGORIES.items():
            if code in code_range:
                return category
    except (ValueError, TypeError):
        pass

    return None
