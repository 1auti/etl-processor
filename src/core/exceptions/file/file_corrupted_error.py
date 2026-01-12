
from core.exceptions.file.file_error import FileError


class FileCorruptedError(FileError()):
    """EL archivo esta corrupto"""
    pass
