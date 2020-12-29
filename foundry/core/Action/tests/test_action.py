

from foundry.core.Action.Action import Action
from foundry.core.Observables.Observable import Observable


def test_initializing():
    """Tests if an Action can initialize"""
    Action("test", Observable())


def test_reference_name():
    """Tests reference name functionality"""
    action = Action("test", Observable())
    assert "test_action" == action.reference_name
