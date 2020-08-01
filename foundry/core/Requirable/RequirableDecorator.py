"""
Provides a class decorator to help with requiring other methods
"""

from .AbstractRequirableDecorator import AbstractRequirableDecorator
from .Requirable import Requirable


class RequirableDecorator(AbstractRequirableDecorator, Requirable):
    """
    The implementation for a generic requirable decorator
    function: The function being decorated
    requirements: A group of callables that will determine if we should run the function
    determine_if_safe: Returns if it is safe
    attach_requirement: Adds another requirement to be tested
    delete_requirement: Removes a requirement
    """


