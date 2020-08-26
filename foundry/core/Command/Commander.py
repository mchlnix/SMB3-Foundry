

from typing import Optional, Deque
from collections import deque

from .Command import Command


class Commander:
    """A class that keeps track of multiple commands"""
    def __init__(self, name: str = "", commands: Optional[Deque[Command]] = None, max_length: int = 25) -> None:
        self.name = name
        self.stack = commands if commands is not None else deque(maxlen=max_length)
        self.undo_stack = deque(maxlen=max_length)

    def push_command(self, command: Command) -> None:
        """Push a command and clear the undo stack"""
        command.do()
        self.stack.append(command)
        self.undo_stack.clear()

    def undo_command(self) -> None:
        """Undo a command to bring it back to the previous state"""
        try:
            command = self.stack.pop()
        except IndexError:
            return  # nothing to undo

        command.undo()
        self.undo_stack.append(command)

    def redo_command(self) -> None:
        """Redo a command to bring it back to the previous state prior to the undo"""
        try:
            command = self.undo_stack.pop()
        except IndexError:
            return  # nothing to redo

        command.do()
        self.stack.append(command)

    @property
    def reference_name(self) -> str:
        """The alt name of the action"""
        return f"{self.name}_commander"
