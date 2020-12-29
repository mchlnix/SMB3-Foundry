"""
Determines if a variable is valid or not
"""

from typing import Any
from keyword import iskeyword


def is_valid_variable_name(name: Any) -> bool:
    """Determines if a string is a valid variable name"""
    return name.isidentifier() and not iskeyword(name)
