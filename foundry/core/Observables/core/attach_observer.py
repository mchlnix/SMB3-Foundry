

from typing import Callable, Optional, Hashable
from random import randint

from foundry.core.Observables.AbstractObservable import AbstractObservable


def attach_observer(observable: AbstractObservable, observer: Callable, identifier: Optional[Hashable] = None) -> None:
    """
    A function to subscribe an observer to receive updates from the observable.
    If no identifier is provided the function will automatically generate a unique number
    :param observable: The observable to subscribe to
    :param observer: The function that desires to receive the event
    :param identifier: An item used to identify the observer
    """

    while identifier is None:
        if temp_id := randint(0, len(observable.observers) * 0x10) not in observable.observers:
            identifier = temp_id  # The temp_id has a 1/16 of missing, in which it will rerole a random number

    observable.observers.update({identifier: observer})
