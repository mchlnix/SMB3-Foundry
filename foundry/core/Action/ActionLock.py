

from typing import Callable

from .Action import Action
from ..Requirable.AbstractRequirable import AbstractRequirable
from ..Observables.ObservableDecorator import ObservableDecorator


class ActionLock(Action):
    """An action that is locked until requirements are resolved"""

    def __init__(self, name: str, func: Callable, requirable: AbstractRequirable) -> None:
        self.name = name
        self.requirable = requirable

        def action(*args, **kwargs):
            """The action of the object"""
            if self.requirable():
                return func(*args, **kwargs)

        self.observable = ObservableDecorator(action)
