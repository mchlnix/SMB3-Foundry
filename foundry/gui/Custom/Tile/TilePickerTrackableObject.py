
from typing import List, Optional, Union
from PySide2.QtWidgets import QWidget

from foundry.core.Observables.ObservableDecorator import ObservableDecorator
from foundry.core.Action.Action import Action

from .AbstractTile import AbstractTile
from .TileTrackableObject import TileTrackableObject
from ..Tiles.TileSelectorPopup import TileSelectorPopup


class TilePickerTrackableObject(TileTrackableObject):
    """A colored button that pops up a dialog whenever clicked"""
    tile_changed_action: Action  # Updates whenever the index changes

    def __init__(self, parent: Optional[QWidget], name: str, tile: AbstractTile):
        super().__init__(parent, name, tile)

    def _initialize_internal_observers(self):
        """Initializes internal observers for special events"""
        c_name = self.__class__.__name__
        self.single_clicked_action.observer.attach_observer(
            lambda *_: self.call_pop_up(), name=f"{c_name} Create Tile Picker Pop Up")

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
            Action("mouse_moved", ObservableDecorator(lambda pos: pos, f"{name} Mouse Moved")),
            Action("tile_changed", ObservableDecorator(lambda idx: idx, f"{name} Color Updated")),
        ]

    def call_pop_up(self, *_):
        """Calls on a pop up to select a new color"""
        TileSelectorPopup(
            self,
            self.pattern_table,
            self.palette,
            size=self.size,
            action=lambda index: setattr(self, "index", index)
        ).exec_()

    @property
    def index(self) -> int:
        """The index the tile is located in for the tsa"""
        return self.tile.index

    @index.setter
    def index(self, index: int) -> None:
        if index != self.index:
            self.tile.index = index
            self.tile_changed_action(index)
            self.refresh_event_action()
