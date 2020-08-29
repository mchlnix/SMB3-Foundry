

from typing import Callable, List

from foundry.core.Action.Action import Action
from foundry.core.Observables.Observable import Observable
from foundry.core.Requirable.RequirableDecorator import RequirableDecorator
from foundry.core.Command.EventCommander import EventCommander

from .MouseEvent import MouseEvent


class MouseEventCommander(EventCommander):
    """A command object to handle mouse events"""
    def __call__(self, event: MouseEvent) -> None:
        """Accepts a mouse event and calls the corresponding commands"""
        self.action(event)

    def connect_on_click(self, command_name: str, click_type: str, action_name: str = "on_click"):
        """Connects a command to a click"""
        action = Action(action_name, Observable())
        self.connect_command(command_name, action)
        requirable = RequirableDecorator(action)
        requirable.attach_requirement(lambda event: event.button_sender == click_type)
        self.action.observer.attach_observer(requirable)

    def reference_name(self) -> str:
        """The alt name of the action"""
        return f"{self.name}_mouse_commander"
