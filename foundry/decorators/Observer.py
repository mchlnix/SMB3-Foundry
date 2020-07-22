"""
Provides a class to help with observing events
"""


from typing import Callable


class Observed:
    """A class that is observable"""
    def __init__(self, function):
        self.function = function
        self.notify_observers = self.notify
        self.attach_observer = self.attach
        self.delete_observer = self.delete
        self.observers = []

    def __call__(self, *args, **kwargs):
        result = self.function(*args, **kwargs)
        self.notify(result)
        return result

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.function}) with observers: {self.observers}"

    def notify(self, result) -> None:
        """Notifies every observer"""
        for observer in self.observers:
            observer(result)

    def attach(self, observer: Callable) -> None:
        """Adds an observer"""
        self.observers.append(observer)

    def delete(self, observer: Callable) -> None:
        """Deletes an observer"""
        self.observers.remove(observer)



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


