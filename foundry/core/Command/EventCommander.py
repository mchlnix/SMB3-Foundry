

from typing import Optional

from foundry.core.Action.Action import Action
from foundry.core.Observables.Observable import Observable
from foundry.core.Command.CommandGroup import CommandGroup
from foundry.core.Command.Commander import Commander
from foundry.core.Command.Command import Command


class EventCommander:
    """A command object to handle mouse events"""
    def __init__(
            self,
            name: str,
            action: Optional[Action] = None,
            commander: Optional[Commander] = None,
            commands: CommandGroup = None
    ) -> None:
        self.name: str = name
        self.action: Action = action if action is not None else Action("event", Observable())
        self.commands: CommandGroup = commands if commands is not None else CommandGroup("")
        self.commander: Commander = commander if commander is not None else Commander("event")

    def __call__(self, *args, **kwargs) -> None:
        """Accepts a mouse event and calls the corresponding commands"""
        self.action(*args, **kwargs)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name}, {self.action}, {self.commander}, {self.commands})"

    def connect_command(self, name: str, action: Action) -> None:
        """Connects a command to the commander"""
        action.observer.attach_observer(lambda *_: self.commander.push_command(self.commands.get_command(name)))

    def add_command(self, name: str, command: Command) -> None:
        """Adds a command to the command group"""
        self.commands.add_command(name, command)

    def undo(self) -> None:
        """Reverts the last command"""
        self.commander.undo_command()

    def redo(self) -> None:
        """Reverts the last revert command"""
        self.commander.redo_command()

    def reference_name(self) -> str:
        """The alt name of the action"""
        return f"{self.name}_event_commander"
