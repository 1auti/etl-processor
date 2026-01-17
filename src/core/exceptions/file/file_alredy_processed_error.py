from core.exceptions.file.file_error import FileError


class FileAlredyProcessedError(FileError()):
    """El archivo ya fue procesado anteriormente"""
    pass
