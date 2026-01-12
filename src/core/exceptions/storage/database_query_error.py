from core.exceptions.storage.storage_error import StorageError


class DatabaeQueryError(StorageError()):
    """Error al ejecutar una query"""
    pass
