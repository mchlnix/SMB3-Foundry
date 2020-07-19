"""
Provides a class decorator to help with requiring other methods
"""

from typing import Callable, Tuple


class Required:
    """A class that is observable"""
    def __init__(self, function):
        self.function = function
        self.notify_required = self.notify
        self.attach_required = self.attach
        self.observers = []

    def __call__(self, *args, **kwargs):
        if self.notify():
            result = self.function(*args, **kwargs)
            return result
        return False

    def notify(self) -> bool:
        """Notifies every observer and determines if it is safe to continue"""
        for observer in self.observers:
            if not observer():
                return False
        return True

    def attach(self, observer: Callable, *_) -> None:
        """Adds an observer"""
        self.observers.append(observer)


class SmartRequired(Required):
    """Runs code that is required and determines if we should run the main function."""
    def __call__(self, *args, **kwargs):
        safe, reason, additional_info = self.notify()
        if safe:
            result = self.function(*args, **kwargs)
            return result
        return safe, reason, additional_info

    def notify(self) -> Tuple[bool, str, str]:
        """Notifies every observer and determines if it is safe to continue"""
        for observer in self.observers:
            safe, reason, additional_info = observer()
            if not safe:
                return False, reason, additional_info
        return True, '', ''
