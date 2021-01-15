

from typing import Dict, Callable

from foundry.core.Observables.core.attach_observer import attach_observer


class FakeObserver:
    """
    A class to emulate an observer
    """

    def __init__(self, observers: Dict[int, Callable]):
        self.observers = observers


def test_adding_observer_with_hashable():
    observable = FakeObserver({})
    attach_observer(observable, 5, 0)
    assert observable.observers[0] == 5


def test_adding_observer_without_hashable():
    observable = FakeObserver({})
    attach_observer(observable, 5)
    assert len(observable.observers) == 1
    for observer in observable.observers.values():
        assert observer == 5
