"""
This module includes the Requirable
This serves as the base implementation of what requirable does
"""

import logging
import random
from inspect import signature
from typing import Callable, Dict, Optional, Hashable, Any

from .AbstractRequirable import AbstractRequirable
from foundry import log_dir


_logger = logging.getLogger(__name__)
_logger.setLevel(logging.WARNING)
_formatter = logging.Formatter('%(asctime)s | %(name)s |  %(levelname)s: %(message)s')
_handler = logging.FileHandler(f"{log_dir}/requirable.log")
_handler.setFormatter(_formatter)
_logger.addHandler(_handler)


class Requirable(AbstractRequirable):
    """
    The basic implementation of a requirable object
    requirements: A group of callables that will determine if we should run the function
    determine_if_safe: Returns if it is safe
    attach_requirement: Adds another requirement to be tested
    delete_requirement: Removes a requirement
    """
    requirements: Dict

    def __init__(self) -> None:
        super(Requirable, self).__init__()

    def __call__(self, *args, **kwargs) -> Any:
        return AbstractRequirable.__call__(self, *args, **kwargs)

    def main_function(self, *args, **kwargs) -> Any:
        """The function to be ran"""
        return True

    def determine_if_safe(self) -> bool:
        """Determine if it is safe"""
        _logger.debug(f"{self} inquiring {self.requirements.values()}")
        value = True
        keys_to_remove = []
        for key, requirement in self.requirements.items():
            try:
                if not requirement():
                    if len(keys_to_remove) > 0:
                        value = False  # if we found an item that needs to be deleted, remove it
                    else:
                        return False
            except NameError:
                _logger.debug(f"Removed deleted observer with identification {key}")
                keys_to_remove.append(key)  # the observer no longer exists
            except TypeError as err:
                _logger.error(f"{err}: {requirement.__name__}{str(signature(requirement))} failed to execute")
                raise TypeError(f"{requirement.__name__}{str(signature(requirement))} failed to execute")

        for key in keys_to_remove:
            #  remove any observer that no longer exists
            self.delete_requirement(key)

        return value

    def attach_requirement(self, requirement: Callable, identifier: Optional[Hashable] = None) -> None:
        """Attach a requirement"""
        if not callable(requirement):
            raise TypeError("Must be callable")
        while identifier is None:
            temp_id = random.randint(10000, 10000000)
            if temp_id not in self.requirements:
                identifier = temp_id

        _logger.debug(f"{self} attached {requirement} with key {identifier} to {self.requirements}")
        self.requirements.update({identifier: requirement})

    def delete_requirement(self, identifier: Hashable) -> None:
        """Removes a requirement"""
        try:
            del self.requirements[identifier]
            _logger.debug(f"{identifier} was deleted from {self.requirements}")
        except KeyError:
            _logger.warning(f"Failed to delete {identifier} from {self.requirements}")