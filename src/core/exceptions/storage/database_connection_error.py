from core.exceptions.storage.storage_error import StorageError


class DatabaseConnectionError(StorageError):
    """Error relacionado no pudo conectarse a la base de datos"""
    pass
