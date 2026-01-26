from .checkpoint_error import CheckpointError


class CheckpointNotFoundError(CheckpointError):
    """No se encontro el checkpoint """
    pass


