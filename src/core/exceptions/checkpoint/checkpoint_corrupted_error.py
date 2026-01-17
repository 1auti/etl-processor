from core.exceptions.checkpoint.checkpoint_error import CheckpointError


class CheckpointCorruptedError(CheckpointError()):
    """EL checkpoint esta corrupto o ilegible"""
    pass


