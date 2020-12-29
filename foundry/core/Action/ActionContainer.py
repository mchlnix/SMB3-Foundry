"""
A container for holding actions to be added and deleted
"""

from typing import Optional, Dict

from foundry.core.Action.Action import Action
from foundry.core.is_valid_variable_name import is_valid_variable_name


class ActionContainer:
    """A container for holding actions"""
    def __init__(self, actions: Optional[Dict]) -> None:
        self.actions = actions

    def add_action(self, action: Action, action_name: Optional[str] = None):
        """Adds an action"""
        if action_name is None:
            self.actions[action.reference_name] = action
        else:
            if is_valid_variable_name(ref_name := f"{action_name}_action"):
                self.actions[ref_name] = action
            else:
                raise SyntaxError(f"Not a valid identifier")

    def add_action_direct(self, action: Action, action_name: Optional[str] = None):
        """Adds an action directly, without putting action suffix it"""
        if action_name is None:
            self.actions[action.name] = action
        else:
            if is_valid_variable_name(action_name):
                self.actions[action] = action
            else:
                raise SyntaxError(f"Not a valid identifier")

    def remove_action(self, action_name: str) -> None:
        """Removes an action"""
        try:
            del self.actions[f"{action_name}_action"]
        except KeyError:
            del self.actions[action_name]

    def add_container(self, container: "ActionContainer") -> None:
        """Adds a container"""
        for key, action in container.actions.items():
            self.add_action_direct(key, action)