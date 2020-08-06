from abc import ABC

from foundry.core.Observables.ObservableDecorator import ObservedAndRequired
from foundry.gui.QMenus import AbstractMenuElement


class MenuElementUpdater(AbstractMenuElement, ABC):
    """A Menu Element that updates all the observers on the action command"""

    def __init__(self, parent, add_action: bool = True) -> None:
        self.action = ObservedAndRequired(self.action)
        super().__init__(parent, add_action)