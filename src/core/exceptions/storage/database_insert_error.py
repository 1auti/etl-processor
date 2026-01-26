from src.core.exceptions.storage.storage_error import StorageError


class DatabaseInsertError(StorageError):
    """No se pudo insertar datos en la base de datos"""
    pass
