

from typing import Optional, Dict

from .Command import Command
from ..Action.Action import Action


class CommandGroup:
    """A group of commands"""
    def __init__(self, name: str, commands: Optional[Dict[str, Command]] = None):
        self.name = name
        self.commands = commands if commands is not None else {}

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name}, {self.commands})"

    def get_command(self, name: str) -> Command:
        """Gets the corresponding command"""
        return self.commands[name]

    def add_command(self, name: str, command: Command) -> None:
        """Adds a command to the command group"""
        self.commands.update({name: command})

    def connect_command(self, name: str, action: Action):
        """Connects a command to a command"""
        command = self.get_command(name)
        action.observer.attach_observer(command.do_action)

    def reference_name(self) -> str:
        """The alt name of the action"""
        return f"{self.name}_command_group"
