

from foundry.core.Observables.AbstractObservable import AbstractObservable


def notify_observers(observable: AbstractObservable, *args, **kwargs) -> None:
    """
    A method to notify all observers for a given observable
    The method automatically passes any additional arguments to the observers as results
    :param observable: The observable that we are wanting to notify observers
    """
    for observer in observable.observers.values():
        observer(*args, **kwargs)
