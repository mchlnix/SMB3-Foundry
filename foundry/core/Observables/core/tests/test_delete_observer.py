

from typing import Dict, Callable

from foundry.core.Observables.core.delete_observer import delete_observer


class FakeObserver:
    """
    A class to emulate an observer
    """

    def __init__(self, observers: Dict[int, Callable]):
        self.observers = observers


def test_deleting_observer():
    observable = FakeObserver({0: None})
    delete_observer(observable, 0)
    assert len(observable.observers) == 0
