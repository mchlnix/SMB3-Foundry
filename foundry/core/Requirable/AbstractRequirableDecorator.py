"""
This module includes the AbstractRequirableDecorator
This serves as the base interface for a requirable decorator
"""

from abc import ABC
from typing import Callable, Any

from .AbstractRequirable import AbstractRequirable


class AbstractRequirableDecorator(AbstractRequirable, ABC):
    """
    The basic interface of a requirable decorator object
    requirements: A group of callables that will determine if we should run the function
    determine_if_safe: Returns if it is safe
    attach_requirement: Adds another requirement to be tested
    delete_requirement: Removes a requirement
    """
    function: Callable

    def __init__(self, function: Callable):
        super(AbstractRequirableDecorator, self).__init__()
        self.function = function

    def main_function(self, *args, **kwargs) -> Any:
        """The function to be ran if everything passed"""
        return self.function(*args, **kwargs)
