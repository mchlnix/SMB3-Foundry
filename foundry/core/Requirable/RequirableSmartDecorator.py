from typing import Tuple

from foundry.core.Requirable.RequirableDecorator import RequirableDecorator


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
        for requirement in self.requirements:
            safe, reason, additional_info = requirement()
            if not safe:
                return False, reason, additional_info
        return True, '', ''