"""
This module includes ObservableDecorator
This serves as a generic implementation of the AbstractObservableDecorator
"""

from typing import Callable

from .AbstractObservableDecorator import AbstractObservableDecorator
from .Observable import Observable


class ObservableDecorator(AbstractObservableDecorator, Observable):
    """
    The implementation for a generic observable decorator
    observables: A group of callables that will be notified of the result
    function: The function being decorated
    notify_observers: Notifies the observables
    attach_observer: Adds a callable to the dict of observables
    delete_observer: Removes a callable to the dict of observables
    """


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
            if isinstance(result, tuple):
                observer(*result)
            else:
                observer(result)

    def attach_observer(self, observer: Callable) -> None:
        """Adds an observer"""
        self.observers.append(observer)

    def delete_observer(self, observer: Callable) -> None:
        """Deletes an observer"""
        self.observers.remove(observer)

    def notify_required(self) -> bool:
        """Notifies every observer and determines if it is safe to continue"""
        for observer in self.required:
            if not observer():
                return False
        return True

    def attach_required(self, observer: Callable, *_) -> None:
        """Adds an observer"""
        self.required.append(observer)

    def delete_required(self, observer: Callable, *_) -> None:
        """Removes a required"""
        self.required.remove(observer)