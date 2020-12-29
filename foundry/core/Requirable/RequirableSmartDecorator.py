from typing import Tuple
from inspect import signature

from foundry.core.Requirable.RequirableDecorator import RequirableDecorator
from foundry.core.Requirable.Requirable import _logger


class SmartRequirableDecorator(RequirableDecorator):
    """Runs code that is required and determines if we should run the main function."""
    def __call__(self, *args, **kwargs):
        safe, reason, additional_info = self.determine_if_safe()
        if safe:
            result = self.function(*args, **kwargs)
            return result
        return safe, reason, additional_info

    def determine_if_safe(self) -> Tuple[bool, str, str]:
        """Notifies every observer and determines if it is safe to continue"""
        _logger.debug(f"{self} inquiring {self.requirements.values()}")
        value, reason, additional_info = True, "", ""

        keys_to_remove = []
        for key, requirement in self.requirements.items():
            try:
                safe, reason, additional_info = requirement()
                if not safe:
                    return safe, reason, additional_info
            except NameError:
                _logger.debug(f"Removed deleted observer with identification {key}")
                keys_to_remove.append(key)  # the observer no longer exists
            except TypeError:
                raise TypeError(f"{requirement.__name__}{str(signature(requirement))} failed to execute")

        for key in keys_to_remove:
            #  remove any observer that no longer exists
            self.delete_requirement(key)

        return value, reason, additional_info
