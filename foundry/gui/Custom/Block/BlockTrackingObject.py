
"""
This module includes the BlockTrackingObject
BlockWidget: A BlockWidget that handles button input
"""

from typing import Optional, List

from PySide2.QtWidgets import QWidget

from foundry.core.Action.Action import Action
from foundry.core.Observables.ObservableDecorator import ObservableDecorator

from foundry.gui.QCore.Tracker import PartialTrackingObject
from foundry.gui.Custom.Block.BlockWidget import BlockWidget

from .AbstractBlock import AbstractBlock


class BlockTrackingObject(PartialTrackingObject, BlockWidget):
    """A Block that acts like a button"""

    def __init__(
            self,
            parent: Optional[QWidget],
            name: str,
            block: AbstractBlock
    ) -> None:
        BlockWidget.__init__(self, parent, name, block)
        PartialTrackingObject.__init__(self)

    def get_actions(self) -> List[Action]:
        """Gets the actions for the object"""
        return [
            Action("refresh_event", ObservableDecorator(lambda *_: self.update())),
            Action("size_update", ObservableDecorator(lambda size: size)),
            Action("pressed", ObservableDecorator(lambda button: button)),
            Action("released", ObservableDecorator(lambda button: button)),
            Action("single_clicked", ObservableDecorator(lambda button: button)),
            Action("double_clicked", ObservableDecorator(lambda button: button)),
            Action("mouse_moved", ObservableDecorator(lambda pos: pos))
        ]
