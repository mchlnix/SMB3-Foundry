

import sys

from foundry.core.Observables.ObservableDecorator import ObservableDecorator


_module = sys.modules[__name__]
_dummy_value = None  # used for testing


def test_initialization():
    """Tests if the observable can initialize"""
    subject = ObservableDecorator(lambda value: value)
    assert isinstance(subject, ObservableDecorator)


def test_attach_observer():
    """Tests if we can attach an observer"""
    subject = ObservableDecorator(lambda value: value)
    subject.attach_observer(lambda value: value, 0)
    assert 0 in subject.observers


def test_attach_random_observer():
    """Tests if we can attach an observer without specifying a key"""
    subject = ObservableDecorator(lambda value: value)
    subject.attach_observer(lambda value: value)
    assert len(subject.observers) == 1


def test_attach_multiple_observers():
    """Tests if we can attach multiple observers"""
    subject = ObservableDecorator(lambda value: value)
    for _ in range(10):
        subject.attach_observer(lambda value: value)
    assert len(subject.observers) == 10


def test_attach_object_that_was_deleted():
    """Tests what happens if a class observer is deleted"""
    class TestClass:
        """A basic class"""
        def test_func(self, value):
            """A function that does something"""
            return value

    subject = ObservableDecorator(lambda value: value)
    test = TestClass()
    subject.attach_observer(lambda value: test.test_func(value))
    del test
    subject(0)


def test_no_same_id():
    """Tests if observable can only have one id"""
    subject = ObservableDecorator(lambda value: value)
    subject.attach_observer(lambda value: value, 0)
    subject.attach_observer(lambda value: value, 0)
    assert len(subject.observers) == 1


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


def test_verify_function_call():
    """Tests if the observer calls the function"""
    global _dummy_value
    _dummy_value = None
    subject = ObservableDecorator(lambda value: value)
    subject.attach_observer(lambda value: setattr(_module, "_dummy_value", value), 0)
    subject.notify_observers(True)
    assert _dummy_value is True


def test_observer_deletion():
    """Tests if we can delete an observer"""
    subject = ObservableDecorator(lambda value: value)
    subject.attach_observer(lambda value: value, 0)
    subject.delete_observable(0)
    assert len(subject.observers) == 0

