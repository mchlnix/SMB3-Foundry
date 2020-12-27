"""
This module includes the BlockWidget
BlockWidget: A widget that handles a Block in terms of Qt space
"""


from typing import Optional, List
from PySide2.QtCore import QSize
from PySide2.QtWidgets import QWidget, QGridLayout
from PySide2.QtGui import QPaintEvent, QPainter

from foundry.core.Action.Action import Action
from foundry.core.Action.AbstractActionObject import AbstractActionObject

from foundry.gui.QWidget import Widget

from foundry.game.gfx.PatternTableHandler import PatternTableHandler
from foundry.game.gfx.Palette import PaletteSet
from foundry.game.gfx.drawable.Tile import Tile as MetaTile

from foundry.core.Observables.ObservableDecorator import ObservableDecorator
from foundry.core.geometry.Position.Position import Position
from foundry.core.geometry.Size.Size import Size

from .AbstractBlock import AbstractBlock

from foundry.gui.Custom.Tile.TilePickerTrackableObject import TilePickerTrackableObject
from foundry.gui.Custom.Tile.Tile import Tile


class BlockTileTrackableObject(Widget, AbstractActionObject):
    """A class for keeping track of a Block"""
    refresh_event_action: Action  # Used internally for redrawing the widget
    size_update_action: Action  # Updates when the size updates
    palette_set_update_action: Action  # Updates whenever the palette set updates
    pattern_table_update_action: Action  # Updates whenever the pattern table updates
    tsa_data_update_action: Action  # Updates whenever the tsa data updates
    index_update_action: Action  # Updates whenever the index updates

    def __init__(
            self,
            parent: Optional[QWidget],
            name: str,
            block: AbstractBlock
    ) -> None:
        Widget.__init__(self, parent)
        AbstractActionObject.__init__(self)
        self.name = name
        self.block = block

        self._set_up_layout()
        self._initialize_internal_observers()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.parent}, {self.name}, {self.index}, {self.pattern_table}, " \
               f"{self.palette_set}, {self.tsa_offset})"

    @property
    def index(self) -> int:
        """The index the block is located in for the tsa"""
        return self.block.index

    @index.setter
    def index(self, index: int) -> None:
        if self.block.index != index:
            self.block.index = index
            self.index_update_action(self.index)

    @property
    def size(self) -> Size:
        """The size of the block in units of 16 pixels"""
        return self.block.size

    @size.setter
    def size(self, size: Size) -> None:
        if self.size != size:
            self.block.size = size
            self.size_update_action(self.size)

    @property
    def tsa_data(self) -> bytearray:
        """Find the tsa data from a given offset"""
        return self.block.tsa_data

    @tsa_data.setter
    def tsa_data(self, tsa_data: bytearray) -> None:
        if self.tsa_data != tsa_data:
            self.block.tsa_data = tsa_data
            self.tsa_data_update_action(self.tsa_data)

    @property
    def pattern_table(self) -> PatternTableHandler:
        """The pattern table for the tiles"""
        return self.block.pattern_table

    @pattern_table.setter
    def pattern_table(self, pattern_table: PatternTableHandler) -> None:
        if self.pattern_table != pattern_table:
            self.block.pattern_table = pattern_table
            self.pattern_table_update_action(self.pattern_table)

    @property
    def palette_set(self) -> PaletteSet:
        """The palette currently used by the tsa"""
        return self.block.palette_set

    @palette_set.setter
    def palette_set(self, palette_set: PaletteSet) -> None:
        if self.palette_set != palette_set:
            self.block.palette_set = palette_set
            self.palette_set_update_action(self.palette_set)

    @property
    def transparency(self) -> bool:
        """Determines if the blocks will be transparent"""
        return self.block.transparency

    @transparency.setter
    def transparency(self, transparency: bool) -> None:
        self.block.transparency = transparency
        self.refresh_event_action()

    def get_actions(self) -> List[Action]:
        """Gets the actions for the object"""
        name = self.__class__.__name__
        return [
            Action("refresh_event", ObservableDecorator(lambda *_: self.update(), f"{name} Refreshed")),
            Action("size_update", ObservableDecorator(lambda size: size, f"{name} Size Updated")),
            Action("palette_set_update", ObservableDecorator(
                lambda palette_set: palette_set, name=f"{name} Palette Set Updated"
            )),
            Action("pattern_table_update", ObservableDecorator(
                lambda pattern_table: pattern_table, name=f"{name} Pattern Table Updated"
            )),
            Action("tsa_data_update", ObservableDecorator(lambda tsa_data: tsa_data, name=f"{name} TSA Data Updated")),
            Action("index_update", ObservableDecorator(lambda index: index, name=f"{name} Index Updated"))
        ]

    def _set_up_layout(self) -> None:
        """Returns the widgets layout"""
        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(0)
        grid.setVerticalSpacing(0)

        self.tiles = []
        for idx in range(4):
            tile = TilePickerTrackableObject(self, "Tile", Tile(
                self.size,
                self.tsa_data[(idx * 0x100) + self.index],
                self.pattern_table,
                self.palette_set[self.index // 0x40]
            ))
            x, y = idx & 1, idx // 2
            grid.addWidget(tile, x, y)
            self.tiles.append(tile)

        self.setLayout(grid)

    def _initialize_internal_observers(self) -> None:
        """Initializes internal observers for special events"""
        name = self.__class__.__name__

        def push_value_to_tile_closure(index: int, var_name: str):
            """Pushes a value to a tile closure"""
            def push_value_to_tile(value):
                """Pushes a value to a tile"""
                setattr(self.tiles[index], var_name, value)
            return push_value_to_tile

        def push_palette_to_tile_closure(index: int):
            """Pushes a palette to a tile closure"""
            def push_palette_to_tile(palette_set: PaletteSet):
                """Pushes a palette to a tile"""
                self.tiles[index].palette = palette_set[self.index // 0x40]
            return push_palette_to_tile

        def push_pattern_to_tile_closure(index: int):
            """Pushes a pattern to a tile closure"""
            def push_pattern_to_tile(*_):
                """Pushes a pattern to a tile"""
                self.tiles[index].index = self.tsa_data[self.index + (index * 0x100)]
            return push_pattern_to_tile

        def update_tsa_data_closure(tile_index: int):
            """Returns the tsa from a change from a given tile_index"""
            def update_tsa_data(index: int):
                """Updates the tsa data from by setting it to a new index"""
                self.tsa_data[self.index + (tile_index * 0x100)] = index
                self.tsa_data_update_action(self.tsa_data)
            return update_tsa_data

        for idx, tile in enumerate(self.tiles):
            self.size_update_action.observer.attach_observer(
                push_value_to_tile_closure(idx, "size"), name=f"{name} Push Size to Tile {idx}"
            )
            self.palette_set_update_action.observer.attach_observer(
                push_palette_to_tile_closure(idx), name=f"{name} Push Palette to Tiles"
            )
            self.pattern_table_update_action.observer.attach_observer(
                push_value_to_tile_closure(idx, "pattern_table"), name=f"{name} Push Pattern Table to Tiles"
            )
            self.tsa_data_update_action.observer.attach_observer(
                push_pattern_to_tile_closure(idx), name=f"{name} Push Index to Tiles"
            )
            self.index_update_action.observer.attach_observer(
                push_pattern_to_tile_closure(idx), name=f"{name} Push Index to Tiles"
            )

            tile.tile_changed_action.observer.attach_observer(
                update_tsa_data_closure(idx), name=f"{tile.__class__.__name__} Push Index to {name}"
            )
