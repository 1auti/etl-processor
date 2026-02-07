from src.core.exceptions.configuration.configuration_error import ConfigurationError


class MissingConfigError(ConfigurationError):
    """Falta una configuracion requerida"""
