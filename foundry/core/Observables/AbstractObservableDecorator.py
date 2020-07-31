"""
This module includes the AbstractObservableDecorator
This serves as the base interface for a observable decorator
"""

from abc import ABC
from typing import Callable

from .AbstractObservable import AbstractObservable


class AbstractObservableDecorator(AbstractObservable, ABC):
    """
    The interface for decorating a function to be an observable
    observables: A group of callables that will be notified of the result
    notify_observers: Notifies the observables
    attach_observer: Adds a callable to the dict of observables
    delete_observer: Removes a callable to the dict of observables
    """
    function: Callable

    def __init__(self, function: Callable):
        super(AbstractObservableDecorator, self).__init__()
        self.function = function

    def __call__(self, *args, **kwargs) -> None:
        result = self.function(*args, **kwargs)
        super(AbstractObservableDecorator, self).__call__(result)
        return result
