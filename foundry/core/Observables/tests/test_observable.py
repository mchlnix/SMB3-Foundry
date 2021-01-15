

from foundry.core.Observables.Observable import Observable


class State:
    """A basic class to implement a state"""
    def __init__(self):
        self.state = False


def test_observable_name():
    observable = Observable(
        lambda: None,
        lambda: None,
        lambda: None,
        "test"
    )
    assert observable.name == "test"


def test_observable_notify_observers():
    state = State()
    observable = Observable(
        lambda *_: setattr(state, "state", True),
        lambda: None,
        lambda: None,
        "test"
    )
    observable.notify_observers(None)
    assert state


def test_observable_attach_observers():
    state = State()
    observable = Observable(
        lambda: None,
        lambda *_: setattr(state, "state", True),
        lambda: None,
        "test"
    )
    observable.attach_observer(None, None)
    assert state


def test_observable_delete_observers():
    state = State()
    observable = Observable(
        lambda: None,
        lambda: None,
        lambda *_: setattr(state, "state", True),
        "test"
    )
    observable.delete_observable(None)
    assert state
