

from typing import Any, Hashable, Optional, Callable

from .AbstractObservable import AbstractObservable


class Observable(AbstractObservable):
    """
    A generic implementation of the AbstractObservable that uses dependency injection
    name: A name to help with debugging and identifying a specific observable
    observables: A group of callables that will be notified of the result
    notify_observers: Notifies the observables
    attach_observer: Adds a callable to the dict of observables
    delete_observer: Removes a callable to the dict of observables
    """

    def __init__(
            self,
            notify_observers: Callable,
            attach_observers: Callable,
            delete_observers: Callable,
            name: str = None
    ):
        self._notify_observers = notify_observers
        self._attach_observers = attach_observers
        self._delete_observers = delete_observers
        super().__init__(name)

    def notify_observers(self, *args, **kwargs) -> None:
        """Update all the observers"""
        self._notify_observers(*args, **kwargs)

    def attach_observer(self, observer: Callable, identifier: Optional[Hashable] = None) -> None:
        """Attach an observer"""
        self._attach_observers(observer, identifier)

    def delete_observable(self, identifier: Hashable) -> None:
        """Removes an observer"""
        self._delete_observers(identifier)
