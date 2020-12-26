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
        self.block.index = index
        self.index_update_action(self.index)

    @property
    def size(self) -> Size:
        """The size of the block in units of 16 pixels"""
        return self.block.size

    @size.setter
    def size(self, size: Size) -> None:
        self.block.size = size
        self.size_update_action(self.size)

    @property
    def tsa_data(self) -> bytearray:
        """Find the tsa data from a given offset"""
        return self.block.tsa_data

    @tsa_data.setter
    def tsa_data(self, tsa_data: bytearray) -> None:
        self.block.tsa_data = tsa_data
        self.tsa_data_update_action(self.tsa_data)

    @property
    def pattern_table(self) -> PatternTableHandler:
        """The pattern table for the tiles"""
        return self.block.pattern_table

    @pattern_table.setter
    def pattern_table(self, pattern_table: PatternTableHandler) -> None:
        self.block.pattern_table = pattern_table
        self.pattern_table_update_action(self.pattern_table)

    @property
    def palette_set(self) -> PaletteSet:
        """The palette currently used by the tsa"""
        return self.block.palette_set

    @palette_set.setter
    def palette_set(self, palette_set: PaletteSet) -> None:
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

        top_left_spinner = TilePickerTrackableObject(self, "Upper Left Tile", Tile(
            self.size, self.tsa_data[self.index], self.pattern_table, self.palette_set[self.index]
        ))
        grid.addWidget(top_left_spinner, 0, 0)

        top_right_spinner = TilePickerTrackableObject(self, "Upper Right Tile", Tile(
            self.size, self.tsa_data[self.index + 0x200], self.pattern_table, self.palette_set[self.index]
        ))
        grid.addWidget(top_right_spinner, 0, 1)

        bottom_left_spinner = TilePickerTrackableObject(self, "Bottom Left Tile", Tile(
            self.size, self.tsa_data[self.index + 0x100], self.pattern_table, self.palette_set[self.index]
        ))
        grid.addWidget(bottom_left_spinner, 1, 0)

        bottom_right_spinner = TilePickerTrackableObject(self, "Bottom Right Tile", Tile(
            self.size, self.tsa_data[self.index + 0x300], self.pattern_table, self.palette_set[self.index]
        ))
        grid.addWidget(bottom_right_spinner, 1, 1)

        self.tiles = [top_left_spinner, bottom_left_spinner, top_right_spinner, bottom_right_spinner]
        self.setLayout(grid)

    def _initialize_internal_observers(self) -> None:
        """Initializes internal observers for special events"""
        name = self.__class__.__name__
        self.size_update_action.observer.attach_observer(self.refresh_event_action, name=f"{name} Refresh Widget")
        self.size_update_action.observer.attach_observer(
            lambda size: self._push_tile_sizes(size), name=f"{name} Push Size to Tiles"
        )
        self.palette_set_update_action.observer.attach_observer(
            lambda palette_set: self._push_tile_palette(palette_set), name=f"{name} Push Palette to Tiles"
        )
        self.pattern_table_update_action.observer.attach_observer(
            lambda pattern_table: self.push_tile_pattern_table(pattern_table),
            name=f"{name} Push Pattern Table to Tiles"
        )
        self.tsa_data_update_action.observer.attach_observer(
            lambda tsa_data: self._push_tile_index_update(), name=f"{name} Push Index to Tiles"
        )
        self.index_update_action.observer.attach_observer(
            lambda index: self._push_tile_index_update(), name=f"{name} Push Index to Tiles"
        )

        def update_tsa_data_closure(tile_index: int):
            """Returns the tsa from a change from a given tile_index"""
            def update_tsa_data(index: int):
                """Updates the tsa data from by setting it to a new index"""
                self.tsa_data[self.index + (tile_index * 0x100)] = index
                self.tsa_data_update_action(self.tsa_data)
            return update_tsa_data
        for idx, tile in enumerate(self.tiles):
            tile.tile_changed_action.observer.attach_observer(
                update_tsa_data_closure(idx), name=f"{tile.__class__.__name__} Push Index to {name}"
            )

    def _push_tile_sizes(self, size) -> None:
        """Updates the sizes of the tiles"""
        for tile in self.tiles:
            tile.size = size

    def _push_tile_palette(self, palette_set: PaletteSet) -> None:
        """Updates the palette of the tiles"""
        for tile in self.tiles:
            tile.palette = palette_set[self.index // 0x40]

    def push_tile_pattern_table(self, pattern_table: PatternTableHandler) -> None:
        """Updates the pattern table of the tiles"""
        for tile in self.tiles:
            tile.pattern_table = pattern_table

    def _push_tile_index_update(self) -> None:
        """Pushes the tile data to the tiles"""
        for idx, tile in enumerate(self.tiles):
            tile.index = self.tsa_data[self.index + (idx * 0x100)]

    def sizeHint(self):
        """The ideal size of the widget"""
        return QSize(MetaTile.image_length * self.size.width * 2, MetaTile.image_height * self.size.height * 2)

    def paintEvent(self, event: QPaintEvent) -> None:
        """Paints the widget"""
        painter = QPainter(self)
        self.block.draw(painter, Position(0, 0))
        super().paintEvent(event)
