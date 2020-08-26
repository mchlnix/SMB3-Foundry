

from foundry.core.Action.Action import Action
from foundry.core.Command.Command import Command
from foundry.core.Observables.Observable import Observable


def test_initializing():
    """Tests if an Action can initialize"""
    Command("test", Action("do", Observable()), Action("undo", Observable()))


def test_reference_name():
    """Tests reference name functionality"""
    command = Command("test", Action("do", Observable()), Action("undo", Observable()))
    assert "test_command" == command.reference_name
