

from foundry.core.Action.ActionLock import ActionLock
from foundry.core.Requirable.Requirable import Requirable


variable_for_testing = True


def new_test_case():
    """Makes a new instance of ActionLock to be tested"""
    return ActionLock("test", change_variable_for_testing, Requirable())


def get_var_for_testing():
    """A function that returns the variable for testing"""
    return variable_for_testing


def change_variable_for_testing(specific_value=None):
    """A test function to test if specific elements of a function are ran"""
    global variable_for_testing
    if specific_value is None:
        variable_for_testing = specific_value
    else:
        variable_for_testing = not variable_for_testing


def test_initialization():
    """Tests if the ActionLock initializes"""
    new_test_case()


def test_reference_name():
    """Tests reference name functionality"""
    action = new_test_case()
    assert "test_action" == action.reference_name


def test_attach_requirement():
    """Tests if a requirement can be added"""
    action = new_test_case()
    action.requirable.attach_required(lambda *_: False)
    assert 1 == len(action.requirable.requirements)


def test_function_called():
    """Tests if the function is called"""
    global variable_for_testing
    variable_for_testing = True
    action = new_test_case()
    action.observable()
    assert not variable_for_testing


def test_lock_on_function():
    """Tests if the function is locked out"""
    global variable_for_testing
    variable_for_testing = True
    action = new_test_case()
    action.requirable.attach_required(lambda *_: get_var_for_testing())
    action.observable()
    action.observable()
    assert not variable_for_testing
