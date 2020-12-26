"""
This module includes the TileWidget
TileWidget: A widget that handles a Tile in terms of Qt space
"""


from typing import Optional, List
from PySide2.QtCore import QSize
from PySide2.QtWidgets import QWidget
from PySide2.QtGui import QPaintEvent, QPainter

from foundry.core.Action.Action import Action
from foundry.core.Action.AbstractActionObject import AbstractActionObject

from foundry.gui.QWidget import Widget

from foundry.game.gfx.PatternTableHandler import PatternTableHandler
from foundry.game.gfx.Palette import Palette
from foundry.game.gfx.drawable.Tile import Tile as MetaTile

from foundry.core.Observables.ObservableDecorator import ObservableDecorator
from foundry.core.geometry.Position.Position import Position
from foundry.core.geometry.Size.Size import Size

from .AbstractTile import AbstractTile


class TileWidget(Widget, AbstractActionObject):
    """A class for keeping track of a Tile"""
    refresh_event_action: Action  # Used internally for redrawing the widget
    block_update_action: Action  # Updates whenever something that defines the block changes
    size_update_action: Action  # Updates when the size updates

    def __init__(
            self,
            parent: Optional[QWidget],
            name: str,
            tile: AbstractTile
    ) -> None:
        Widget.__init__(self, parent)
        AbstractActionObject.__init__(self)
        self.name = name
        self.tile = tile

        self._initialize_internal_observers()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.parent}, {self.name}, {self.index}, {self.pattern_table}, " \
               f"{self.palette_set}, {self.tsa_offset})"

    @property
    def index(self) -> int:
        """The index the tile is located in for the tsa"""
        return self.tile.index

    @index.setter
    def index(self, index: int) -> None:
        self.tile.index = index
        self.refresh_event_action()

    @property
    def size(self) -> Size:
        """The size of the tile in units of 8 pixels"""
        return self.block.size

    @size.setter
    def size(self, size: Size) -> None:
        self.tile.size = size
        self.size_update_action(self._size)

    @property
    def pattern_table(self) -> PatternTableHandler:
        """The pattern table for the tiles"""
        return self.tile.pattern_table

    @pattern_table.setter
    def pattern_table(self, pattern_table: PatternTableHandler) -> None:
        self.tile.pattern_table = pattern_table
        self.refresh_event_action()

    @property
    def palette(self) -> Palette:
        """The palette currently used"""
        return self.tile.palette

    @palette.setter
    def palette(self, palette: Palette) -> None:
        self.tile.palette = palette
        self.refresh_event_action()

    @property
    def transparency(self) -> bool:
        """Determines if the tile will be transparent"""
        return self.tile.transparency

    @transparency.setter
    def transparency(self, transparency: bool) -> None:
        self.tile.transparency = transparency
        self.refresh_event_action()

    def get_actions(self) -> List[Action]:
        """Gets the actions for the object"""
        name = self.__class__.__name__
        return [
            Action("refresh_event", ObservableDecorator(lambda *_: self.update(), f"{name} Refreshed")),
            Action("size_update", ObservableDecorator(lambda size: size, f"{name} Size Updated"))
        ]

    def _initialize_internal_observers(self) -> None:
        """Initializes internal observers for special events"""
        self.size_update_action.observer.attach_observer(self.refresh_event_action)

    def sizeHint(self):
        """The ideal size of the widget"""
        return QSize(MetaTile.image_length * self.size.width, MetaTile.image_height * self.size.height)

    def paintEvent(self, event: QPaintEvent) -> None:
        """Paints the widget"""
        painter = QPainter(self)
        self.tile.draw(painter, Position(0, 0))
        super().paintEvent(event)
