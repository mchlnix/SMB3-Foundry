

from typing import Optional, List
from PySide2.QtWidgets import QWidget, QGridLayout
from PySide2.QtGui import Qt

from foundry.core.Settings.util import get_setting
from foundry.core.geometry.Size.Size import Size
from foundry.core.Observables.ObservableDecorator import ObservableDecorator
from foundry.core.Action.Action import Action
from foundry.core.Action.AbstractActionObject import AbstractActionObject

from foundry.gui.QCore.palette import DEFAULT_PALETTE
from foundry.gui.QCore.pattern_table import PATTERN_TBL_DEFAULT
from foundry.gui.QCore import MARGIN_TIGHT
from foundry.gui.QWidget import Widget
from foundry.gui.Custom.Tile.Tile import Tile
from foundry.gui.Custom.Tile.TileTrackableObject import TileTrackableObject

from foundry.game.gfx.PatternTableHandler import PatternTableHandler
from foundry.game.gfx.Palette import Palette


class TileSelector(Widget, AbstractActionObject):
    """A class for selecting a Tile"""
    def __init__(
            self,
            parent: Optional[QWidget],
            size: Optional[Size],
            pattern_table: Optional[PatternTableHandler] = None,
            palette: Optional[Palette] = DEFAULT_PALETTE
    ) -> None:
        Widget.__init__(self, parent)
        AbstractActionObject.__init__(self)
        if pattern_table is None:
            pattern_table = PatternTableHandler(PATTERN_TBL_DEFAULT)
        self._size = size
        self._pattern_table = pattern_table
        self._palette = palette

        self._set_up_layout()

    def _set_up_layout(self) -> None:
        """Returns the widgets layout"""

        def closure(i):
            """Keep the idx in scope"""
            return lambda *_: self.single_clicked_action(i)

        self.tiles = []
        grid_layout = QGridLayout()
        grid_layout.setSpacing(MARGIN_TIGHT)
        grid_layout.setDefaultPositioning(0x10, Qt.Horizontal)
        for idx in range(1, 0x100):
            tiles = TileTrackableObject(
                self, f"Tile {idx}", Tile(self.size, idx, self.pattern_table, self.palette, self.transparency)
            )
            tiles.single_clicked_action.observer.attach_observer(closure(idx))
            self.tiles.append(tiles)
            grid_layout.addWidget(tiles)

        self.setLayout(grid_layout)

    def get_actions(self) -> List[Action]:
        """Gets the actions for the object"""
        name = self.__class__.__name__
        return [
            Action("refresh_event", ObservableDecorator(lambda *_: self.update(), f"{name} Refreshed")),
            Action("size_update", ObservableDecorator(lambda size: size, f"{name} Size Updated")),
            Action("palette_update", ObservableDecorator(lambda palette: palette, f"{name}Palette Updated")),
            Action("pattern_table_update", ObservableDecorator(
                lambda pattern_table: pattern_table, f"{name} Pattern Table Updated"
            )),
            Action("single_clicked", ObservableDecorator(lambda button: button, f"{name} Single Clicked")),
        ]

    @property
    def size(self) -> Size:
        """The size of the blocks"""
        return self._size

    @size.setter
    def size(self, size: Size) -> None:
        self._size = size
        for tile in self.tile:
            tile.size = size
        self.size_update_action(self._size)
        self.refresh_event_action()

    @property
    def pattern_table(self) -> PatternTableHandler:
        """Displays the current page of graphics"""
        return self._pattern_table

    @pattern_table.setter
    def pattern_table(self, pattern_table: PatternTableHandler) -> None:
        self._pattern_table = pattern_table
        for tile in self.tile:
            tile.pattern_table = pattern_table
        self.pattern_table_update_action(self._pattern_table)
        self.refresh_event_action()

    @property
    def palette(self) -> Palette:
        """Determines the colors of the tiles displayed"""
        return self._palette

    @palette.setter
    def palette(self, palette: Palette) -> None:
        self._palette = palette
        for tile in self.tile:
            tile.palette_set = palette
        self.palette_update_action(self._palette)
        self.refresh_event_action()

    @property
    def transparency(self) -> bool:
        """Determines if the tile will be transparent"""
        return get_setting("block_transparency", True)