

from abc import abstractmethod
from typing import Callable, Any, Dict, Optional, Hashable


class AbstractObservable:
    """
    The basic interface of an observable object
    name: A name to help with debugging and identifying a specific observable
    observables: A group of callables that will be notified of the result
    notify_observers: Notifies the observables
    attach_observer: Adds a callable to the dict of observables
    delete_observer: Removes a callable to the dict of observables
    """
    observers: Dict

    def __init__(self, name: str = None) -> None:
        self.name = self.__class__.__name__ if name is None else name
        self.observers = {}

    def __call__(self, *args, **kwargs):
        self.notify_observers(*args, **kwargs)

    def __str__(self) -> str:
        """The name that shows up in debugging"""
        return self.name

    @abstractmethod
    def notify_observers(self, result: Any) -> None:
        """Update all the observers"""

    @abstractmethod
    def attach_observer(self, observer: Callable, identifier: Optional[Hashable] = None) -> None:
        """Attach an observer"""

    @abstractmethod
    def delete_observable(self, identifier: Hashable) -> None:
        """Removes an observer"""
