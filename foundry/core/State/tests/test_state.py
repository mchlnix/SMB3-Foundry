

from foundry.core.Action.Action import Action
from foundry.core.State.State import State


class ObserverCallingTest():
    def __init__(self):
        self.state = False

    def __call__(self, value):
        self.state = value


def test_initialization():
    """Tests if the State initializes"""
    State("test", False, Action)


def test_keep_state():
    """Tests if the State keeps state"""
    state = State("test", False, Action)
    assert not state.state


def test_change_state():
    """Tests if the State can change"""
    state = State("test", False, Action)
    assert not state.state
    state.state = not state.state
    assert state.state


def test_call_observable():
    """Tests if the State can update observables"""
    state = State("test", False, Action)
    test = ObserverCallingTest()
    assert not state.state
    state.observer.attach_observer(lambda value: setattr(test, "state", value))
    state.state = not state.state
    assert state.state
    assert test.state
