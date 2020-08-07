

from typing import Callable

from foundry.core.Action.AbstractActionSafe import AbstractActionSafe
from foundry.core.Requirable.RequirableSmartDecorator import SmartRequirableDecorator


TEST_REASON = "test"
TEST_ADDITIONAL = "additional info"


class ActionSafeTest(AbstractActionSafe):
    """A concrete implementation of ActionSafe used for testing"""
    def __init__(self, name: str, func: Callable, proceed: bool = False) -> None:
        AbstractActionSafe.__init__(self, name, func)
        self.proceed = proceed
        self.reason, self.additional_info = None, None

    def proceed_message(self, reason: str, additional_information: str) -> bool:
        """THe proceed message"""
        self.reason, self.additional_info = reason, additional_information
        return self.proceed


class ChangingWarningTest:
    """A warning that changes"""
    def __init__(self, state: bool) -> None:
        self.state = state

    def __call__(self):
        return self.state, TEST_REASON, TEST_ADDITIONAL


def new_test_case():
    """Generates a new test case"""
    return ActionSafeTest("test", lambda *_: True)


def warning_fail():
    """A fake warning that always fails"""
    return False, TEST_REASON, TEST_ADDITIONAL


def warning_succeed():
    """A fake warning that always succeeds"""
    return True, "", ""


def test_initialization():
    """Tests if the object initializes"""
    new_test_case()


def test_reference_name():
    """Tests reference name functionality"""
    action = new_test_case()
    assert "test_action" == action.reference_name


def test_attach_warning():
    """Tests attaching a warning successful"""
    action = new_test_case()
    warning = SmartRequirableDecorator(warning_succeed)
    action.warning_checks.attach_required(warning)
    assert 1 == len(action.warning_checks.requirements)


def test_warning_failing():
    """Tests when a warning returns False"""
    action = new_test_case()
    warning = SmartRequirableDecorator(warning_fail)
    action.warning_checks.attach_required(warning)
    assert not action.observable()


def test_warning_succeeding():
    """Tests when a warning returns True"""
    action = new_test_case()
    warning = SmartRequirableDecorator(warning_succeed)
    action.warning_checks.attach_required(warning)
    assert action.observable()


def test_warning_changing():
    """Tests when a warning fails then succeeds"""
    action = new_test_case()
    warning = ChangingWarningTest(False)
    action.warning_checks.attach_required(warning)
    assert not action.observable()
    warning.state = True
    assert action.observable()


def test_warning_message():
    """Tests warning message is received when failing"""
    action = new_test_case()
    warning = SmartRequirableDecorator(warning_fail)
    action.warning_checks.attach_required(warning)
    action.observable()
    assert TEST_REASON == action.reason
    assert TEST_ADDITIONAL == action.additional_info
