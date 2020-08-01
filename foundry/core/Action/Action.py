

from typing import Optional
from dataclasses import dataclass
from PySide2.QtWidgets import QWidget
from PySide2.QtCore import Signal

from foundry.core.Action.AbstractActionObject import AbstractActionObject
from foundry.core.Observables.Observable import Observable
from foundry.core.Observables.ObservableDecorator import ObservableDecorator


@dataclass
class Action:
    """
    This class provides the basis for chaining actions together and making them inheritable
    name: The name of the action
    observer: The observer be called
    """
    name: str
    observer: Observable

    @property
    def alt_name(self) -> str:
        """The alt name of the action"""
        return f"{self.name}_action"

    @classmethod
    def from_signal(cls, name: str, signal: Signal, pass_result: bool = True) -> "Action":
        """Makes an action from a signal"""
        if pass_result:
            observer = ObservableDecorator(lambda result: result)
        else:
            observer = ObservableDecorator(lambda *_: True)
        signal.connect(observer)
        return Action(name, observer)


class AbstractActionWidget(QWidget, AbstractActionObject):
    """This class acts as a QWidget and keeps all the features of an abstract action object"""
    def __init__(self, parent: Optional[QWidget]) -> None:
        QWidget.__init__(self, parent)
        AbstractActionObject.__init__(self)
