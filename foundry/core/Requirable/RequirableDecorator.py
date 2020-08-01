"""
Provides a class decorator to help with requiring other methods
"""

from typing import Tuple

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


class SmartRequirable(Requirable):
    """Runs code that is required and determines if we should run the main function."""
    def __call__(self, *args, **kwargs):
        safe, reason, additional_info = self.determine_if_safe()
        if safe:
            result = self.function(*args, **kwargs)
            return result
        return safe, reason, additional_info

    def determine_if_safe(self) -> Tuple[bool, str, str]:
        """Notifies every observer and determines if it is safe to continue"""
        for observer in self.observers:
            safe, reason, additional_info = observer()
            if not safe:
                return False, reason, additional_info
        return True, '', ''
