"""
Provides a class to help with observing events
"""


from typing import Callable
from foundry.decorators.Required import Required


class Observed:
    """A class that is observable"""
    def __init__(self, function):
        self.function = function
        self.notify_observers = self.notify
        self.attach_observer = self.attach
        self.observers = []

    def __call__(self, *args, **kwargs):
        result = self.function(*args, **kwargs)
        self.notify(result)
        return result

    def notify(self, result) -> None:
        """Notifies every observer"""
        for observer in self.observers:
            observer(result)

    def attach(self, observer: Callable) -> None:
        """Adds an observer"""
        self.observers.append(observer)


class ObservedAndRequired:
    """A decorator that has required and observed parameters"""
    def __init__(self, function):
        self.function = function
        self.observers = []
        self.required = []

    def __call__(self, *args, **kwargs):
        if self.notify_required():
            result = self.function(*args, **kwargs)
            self.notify_observers(result)
            return result
        return False

    def notify_observers(self, result) -> None:
        """Notifies every observer"""
        for observer in self.observers:
            observer(result)

    def attach_observer(self, observer: Callable) -> None:
        """Adds an observer"""
        self.observers.append(observer)

    def notify_required(self) -> bool:
        """Notifies every observer and determines if it is safe to continue"""
        for observer in self.required:
            if not observer():
                return False
        return True

    def attach_required(self, observer: Callable, *_) -> None:
        """Adds an observer"""
        self.required.append(observer)
