from core.exceptions.etl_exception import EtlException


class CheckpointError(EtlException()):
    """Error relacionado con un checkpoint"""
    pass

