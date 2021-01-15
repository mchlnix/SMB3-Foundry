

from typing import Hashable

from foundry.core.Observables.AbstractObservable import AbstractObservable


def delete_observer(observable: AbstractObservable, identifier: Hashable) -> None:
    """
    A function to unsubscribe an observer from the observable
    :param observable: The observable to unsubscribe to
    :param identifier: The id of the observer that wishes to unsubscribe
    """
    del observable.observers[identifier]
