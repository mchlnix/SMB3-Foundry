"""
This module includes the AbstractRequirable
This serves as the base interface of what requirable does
"""

from abc import abstractmethod
from typing import Callable, Dict, Optional, Hashable, Any


class AbstractRequirable:
    """
    The basic interface of a requirable object
    requirements: A group of callables that will determine if we should run the function
    determine_if_safe: Returns if it is safe
    attach_requirement: Adds another requirement to be tested
    delete_requirement: Removes a requirement
    """
    requirements: Dict

    def __init__(self) -> None:
        self.requirements = {}

    def __call__(self, *args, **kwargs) -> Any:
        if self.determine_if_safe():
            return self.main_function(*args, **kwargs)
        return False

    @abstractmethod
    def main_function(self, *args, **kwargs) -> Any:
        """The function to be ran"""

    @abstractmethod
    def determine_if_safe(self) -> bool:
        """Determine if it is safe"""

    @abstractmethod
    def attach_requirement(self, requirement: Callable, identifier: Optional[Hashable] = None) -> None:
        """Attach an observer"""

    @abstractmethod
    def delete_requirement(self, identifier: Hashable) -> None:
        """Removes an observer"""
