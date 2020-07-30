

import sys

from foundry.core.Observables.Observable import Observable


_module = sys.modules[__name__]
_dummy_value = None  # used for testing


def test_initialization():
    """Tests if the observable can initialize"""
    subject = Observable()
    assert isinstance(subject, Observable)


def test_attach_observer():
    """Tests if we can attach an observer"""
    subject = Observable()
    subject.attach_observer(lambda value: value, 0)
    assert 0 in subject.observers


def test_attach_random_observer():
    """Tests if we can attach an observer without specifying a key"""
    subject = Observable()
    subject.attach_observer(lambda value: value)
    assert len(subject.observers) == 1


def test_attach_multiple_observers():
    """Tests if we can attach multiple observers"""
    subject = Observable()
    for _ in range(10):
        subject.attach_observer(lambda value: value)
    assert len(subject.observers) == 10


def test_no_same_id():
    """Tests if observable can only have one id"""
    subject = Observable()
    subject.attach_observer(lambda value: value, 0)
    subject.attach_observer(lambda value: value, 0)
    assert len(subject.observers) == 1


def test_verify_function_call():
    """Tests if the observer calls the function"""
    global _dummy_value
    _dummy_value = None
    subject = Observable()
    subject.attach_observer(lambda value: setattr(_module, "_dummy_value", value), 0)
    subject.notify_observers(True)
    assert _dummy_value is True


def test_observer_deletion():
    """Tests if we can delete an observer"""
    subject = Observable()
    subject.attach_observer(lambda value: value, 0)
    subject.delete_observable(0)
    assert len(subject.observers) == 0
