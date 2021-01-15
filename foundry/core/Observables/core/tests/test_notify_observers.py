

from typing import Dict, Callable, Any
from dataclasses import dataclass

from foundry.core.Observables.core.notify_observers import notify_observers


@dataclass
class State:
    state: Any


class FakeObserver:
    """
    A class to emulate an observer
    """

    def __init__(self, observers: Dict[int, Callable]):
        self.observers = observers


def test_notifying_observer():
    state = State(False)
    observable = FakeObserver({0: lambda value: setattr(state, "state", value)})
    notify_observers(observable, True)
    assert state.state


def test_notifying_multiple_observers():
    state, other_state = State(False), State(False)
    observable = FakeObserver({
        0: lambda value: setattr(state, "state", value),
        1: lambda value: setattr(other_state, "state", value)
    })
    notify_observers(observable, True)
    assert state.state
    assert other_state.state


def test_sending_args_and_kwargs():
    state = State(0)

    def update_distance_from_origin(x, y):
        state.state = (x ** 2 + y ** 2) ** .5

    observable = FakeObserver({
        0: update_distance_from_origin
    })

    notify_observers(observable, 3, 4)
    assert state.state == 5

    notify_observers(observable, x=5, y=12)
    assert state.state == 13

    notify_observers(observable, 7, y=24)
    assert state.state == 25
