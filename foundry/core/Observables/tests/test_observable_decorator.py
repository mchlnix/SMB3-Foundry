

import sys

from foundry.core.Observables.ObservableDecorator import ObservableDecorator


_module = sys.modules[__name__]
_dummy_value = None  # used for testing


def test_initialization():
    """Tests if the observable can initialize"""
    subject = ObservableDecorator(lambda value: value)
    assert isinstance(subject, ObservableDecorator)


def test_function_decoration():
    """Tests if the decorator can decorate a function"""
    subject = ObservableDecorator(lambda value: value + 1)
    assert subject(1) == 2


def test_verify_decorated_call():
    """Tests if the observer calls the function"""
    global _dummy_value
    _dummy_value = None
    subject = ObservableDecorator(lambda value: not value)
    subject.attach_observer(lambda value: setattr(_module, "_dummy_value", value))
    subject(True)
    assert not _dummy_value
