import structlog


class log_context:
    """
    Context manager para agregar contexto temporal a logs.

    Example:
        >>> logger = get_logger()
        >>> with log_context(file_id="abc123", batch_num=5):
        ...     logger.info("Processing batch")
        # Output incluirá file_id y batch_num automáticamente
    """

    def __init__(self, **kwargs):
        self.context = kwargs
        self.token = None

    def __enter__(self):
        self.token = structlog.contextvars.bind_contextvars(**self.context)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.token:
            structlog.contextvars.unbind_contextvars(*self.context.keys())
