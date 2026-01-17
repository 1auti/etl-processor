

from core.exceptions.file.file_error import FileError


class FilePermissionError(FileError()):
    """No tenes permisos para este archivo"""
    pass
