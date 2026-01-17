"""
Config package exports.
"""

from .config import Config
from .singleton_config import get_config

__all__ = ['Config', 'get_config']
