"""
Provides a context decorator to help with saving and loading settings
"""

from typing import Callable
from functools import wraps

from foundry.gui.settings import load_settings, save_settings


def handle_settings(func: Callable) -> Callable:
    """Returns a function that will load and save the settings"""
    @wraps(func)
    def inner(*args, **kwargs):
        """Loads the settings, runs the function, and saves the settings"""
        load_settings()
        result = func(*args, **kwargs)
        save_settings()
        return result
    return inner
