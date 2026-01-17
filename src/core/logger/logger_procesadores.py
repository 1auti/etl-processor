"""Centralizacion de configuracion de procesadores"""

import logging
import sys
import datetime
from pathlib import Path

def add_log_level(logger, method_name, event_dict):
    """Agregamos el nivel del logs al event_dict"""
    event_dict['level'] = method_name.upper()
    return event_dict

def add_timestamp(logger, method_name, event_dict):
    """Agregamos el timestamp ISO con timezone"""
    event_dict['timestamp'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    return event_dict

def add_caller_info(logger, method_name, event_dict):
    """Agrega información del caller (archivo, línea, función)."""
    import inspect

    # Obtener el frame del caller (saltando frames internos de structlog)
    frame = inspect.currentframe()
    try:
        # Subir en el stack hasta encontrar el caller real
        for _ in range(5):
            frame = frame.f_back
            if frame is None:
                break

            # Ignorar frames internos de logging
            filename = frame.f_code.co_filename
            if 'structlog' not in filename and 'logging' not in filename:
                event_dict['caller'] = {
                    'file': Path(filename).name,
                    'line': frame.f_lineno,
                    'function': frame.f_code.co_name
                }
                break
    finally:
        del frame

    return event_dict





