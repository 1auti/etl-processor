from typing import Dict, Set


class HTTPConstants:
    """Constantes relacionadas con HTTP."""

    # Métodos HTTP válidos
    VALID_METHODS: Set[str] = {
        'GET',
        'POST',
        'PUT',
        'DELETE',
        'PATCH',
        'HEAD',
        'OPTIONS',
        'CONNECT',
        'TRACE'
    }

    # Categorías de códigos de estado
    STATUS_SUCCESS_MIN = 200
    STATUS_SUCCESS_MAX = 299
    STATUS_REDIRECT_MIN = 300
    STATUS_REDIRECT_MAX = 399
    STATUS_CLIENT_ERROR_MIN = 400
    STATUS_CLIENT_ERROR_MAX = 499
    STATUS_SERVER_ERROR_MIN = 500
    STATUS_SERVER_ERROR_MAX = 599

    # Códigos de estado comunes
    STATUS_CODES: Dict[int, str] = {
        # 2xx Success
        200: 'OK',
        201: 'Created',
        202: 'Accepted',
        204: 'No Content',

        # 3xx Redirection
        301: 'Moved Permanently',
        302: 'Found',
        304: 'Not Modified',
        307: 'Temporary Redirect',
        308: 'Permanent Redirect',

        # 4xx Client Errors
        400: 'Bad Request',
        401: 'Unauthorized',
        403: 'Forbidden',
        404: 'Not Found',
        405: 'Method Not Allowed',
        408: 'Request Timeout',
        409: 'Conflict',
        429: 'Too Many Requests',

        # 5xx Server Errors
        500: 'Internal Server Error',
        502: 'Bad Gateway',
        503: 'Service Unavailable',
        504: 'Gateway Timeout'
    }

    # Versiones HTTP soportadas
    VALID_HTTP_VERSIONS: Set[str] = {
        'HTTP/1.0',
        'HTTP/1.1',
        'HTTP/2.0',
        'HTTP/3.0'
    }
