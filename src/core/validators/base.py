"""
Base validators and decorators.
"""

import inspect
from typing import Any, Callable, List


def validate_with(validator_func: Callable, error_message: str = "Validation failed"):
    """
    Decorador para validar parámetros de función.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            for arg in args:
                if not validator_func(arg):
                    raise ValueError(f"{error_message}: {arg}")

            for key, value in kwargs.items():
                if not validator_func(value):
                    raise ValueError(f"{error_message} for '{key}': {value}")

            return func(*args, **kwargs)

        return wrapper

    return decorator


def validate_arguments(**validators):
    """
    Decorador para validar argumentos específicos.
    """

    def decorator(func):
        sig = inspect.signature(func)

        def wrapper(*args, **kwargs):
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            for param_name, validator in validators.items():
                if param_name in bound_args.arguments:
                    value = bound_args.arguments[param_name]
                    if not validator(value):
                        raise ValueError(f"Invalid value for parameter '{param_name}': {value}")

            return func(*args, **kwargs)

        return wrapper

    return decorator


def validate_all(*validators: Callable, value: Any) -> bool:
    """Aplica múltiples validadores a un valor."""
    for validator in validators:
        if not validator(value):
            return False
    return True


def validate_any(*validators: Callable, value: Any) -> bool:
    """Valida si al menos un validador pasa."""
    for validator in validators:
        if validator(value):
            return True
    return False


def get_validation_errors(*validators: Callable, value: Any) -> List[str]:
    """
    Obtiene mensajes de error de todos los validadores que fallan.

    Args:
        *validators: Pares (validator, error_message)
        value: Valor a validar
    """
    errors = []

    for validator, error_msg in validators:
        if not validator(value):
            errors.append(error_msg)

    return errors
