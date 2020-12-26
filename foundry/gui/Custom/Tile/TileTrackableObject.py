
"""
This module includes the TileTrackingObject
TileWidget: A TileWidget that handles button input
"""

from typing import Optional, List

from PySide2.QtWidgets import QWidget

from foundry.core.Action.Action import Action
from foundry.core.Observables.ObservableDecorator import ObservableDecorator

from foundry.gui.QCore.Tracker import PartialTrackingObject
from foundry.gui.Custom.Tile.TileWidget import TileWidget

from .AbstractTile import AbstractTile


class TileTrackableObject(PartialTrackingObject, TileWidget):
    """A Tile that acts like a button"""

    def __init__(
            self,
            parent: Optional[QWidget],
            name: str,
            tile: AbstractTile
    ) -> None:
        TileWidget.__init__(self, parent, name, tile)
        PartialTrackingObject.__init__(self)

    def get_actions(self) -> List[Action]:
        """Gets the actions for the object"""
        name = self.__class__.__name__
        return [
            Action("refresh_event", ObservableDecorator(lambda *_: self.update(), f"{name} Refreshed")),
            Action("size_update", ObservableDecorator(lambda size: size, f"{name} Size Updated")),
            Action("pressed", ObservableDecorator(lambda button: button, f"{name} Pressed")),
            Action("released", ObservableDecorator(lambda button: button, f"{name} Released")),
            Action("single_clicked", ObservableDecorator(lambda button: button, f"{name} Single Clicked")),
            Action("double_clicked", ObservableDecorator(lambda button: button, f"{name} Double Clicked")),
            Action("mouse_moved", ObservableDecorator(lambda pos: pos, f"{name} Mouse Moved"))
        ]
