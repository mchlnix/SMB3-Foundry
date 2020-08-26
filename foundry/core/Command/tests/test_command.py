

from foundry.core.Action.Action import Action
from foundry.core.Command.Command import Command
from foundry.core.Observables.Observable import Observable


def test_initializing():
    """Tests if an Action can initialize"""
    Command("test", Observable(), Observable())


def test_reference_name():
    """Tests reference name functionality"""
    command = Command("test", Observable(), Observable())
    assert "test_command" == command.reference_name
