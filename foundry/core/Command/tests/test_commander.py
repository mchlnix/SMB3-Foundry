

import sys
import pytest
from typing import List

from foundry.core.Command.Command import Command
from foundry.core.Command.Commander import Commander


mod_name = sys.modules[__name__]
test_var: int = 0

getattr(sys.modules[__name__], "test_var")


COMMANDS = [
    Command(
        "add_one",
        lambda *_: setattr(mod_name, "test_var", getattr(mod_name, "test_var") + 1),
        lambda *_: setattr(mod_name, "test_var", getattr(mod_name, "test_var") - 1)
    ),
    Command(
        "divide_in_half",
        lambda *_: setattr(mod_name, "test_var", getattr(mod_name, "test_var") / 2),
        lambda *_: setattr(mod_name, "test_var", getattr(mod_name, "test_var") * 2)
    ),
    Command(
        """subtract_two""",
        lambda *_: setattr(mod_name, "test_var", getattr(mod_name, "test_var") - 2),
        lambda *_: setattr(mod_name, "test_var", getattr(mod_name, "test_var") + 2)
    )
]

COMMANDS_LIST = [
    [COMMANDS[0], COMMANDS[1], COMMANDS[2]],
    [COMMANDS[0], COMMANDS[2], COMMANDS[1]],
    [COMMANDS[1], COMMANDS[2], COMMANDS[0]],
    [COMMANDS[1], COMMANDS[0], COMMANDS[2]],
    [COMMANDS[2], COMMANDS[1], COMMANDS[0]],
    [COMMANDS[2], COMMANDS[0], COMMANDS[1]],
]


def test_initializing():
    """Tests if an Action can initialize"""
    Commander("test")


def test_reference_name():
    """Tests reference name functionality"""
    commander = Commander("test")
    assert "test_commander" == commander.reference_name


@pytest.mark.parametrize('commands', COMMANDS_LIST)
def test_doing_commands(commands: List[Command]):
    """Test doing commands"""
    global test_var
    test_var = 41
    commander = Commander("test")
    for command in commands:
        commander.push_command(command)
    assert test_var != 41


@pytest.mark.parametrize('commands', COMMANDS_LIST)
def test_undoing_commands(commands: List[Command]):
    """Test undoing commands"""
    global test_var
    test_var = 41
    commander = Commander("test")
    for command in commands:
        commander.push_command(command)
    assert test_var != 41

    for _ in commands:
        commander.undo_command()

    assert test_var == 41


@pytest.mark.parametrize('commands', COMMANDS_LIST)
def test_redoing_commands(commands: List[Command]):
    """Test undoing commands"""
    global test_var
    test_var = 41
    commander = Commander("test")
    for command in commands:
        commander.push_command(command)
    result = test_var

    for _ in commands:
        commander.undo_command()
    for _ in commands:
        commander.redo_command()

    assert test_var == result