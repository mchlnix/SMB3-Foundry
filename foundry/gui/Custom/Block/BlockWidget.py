"""
This module includes the BlockWidget
BlockWidget: A widget that handles a Block in terms of Qt space
"""


from typing import Optional, List
from PySide2.QtCore import QSize
from PySide2.QtWidgets import QWidget
from PySide2.QtGui import QPaintEvent, QPainter

from foundry.core.Action.Action import Action
from foundry.core.Action.AbstractActionObject import AbstractActionObject

from foundry.gui.QWidget import Widget

from foundry.game.File import ROM, TSA_TABLE_SIZE, TSA_TABLE_INTERVAL
from foundry.game.gfx.PatternTableHandler import PatternTableHandler
from foundry.game.gfx.Palette import PaletteSet
from foundry.game.gfx.drawable.Block import Block as MetaBlock

from foundry.core.Observables.ObservableDecorator import ObservableDecorator
from foundry.core.geometry.Position.Position import Position
from foundry.core.geometry.Size.Size import Size


class BlockWidget(Widget, AbstractActionObject):
    """A class for keeping track of a Block"""
    refresh_event_action: Action  # Used internally for redrawing the widget
    block_update_action: Action  # Updates whenever something that defines the block changes
    size_update_action: Action  # Updates when the size updates

    def __init__(
            self,
            parent: Optional[QWidget],
            name: str,
            size: Optional[Size],
            index: int,
            ptn_tbl: PatternTableHandler,
            pal_set: PaletteSet,
            tsa_offset: int,
            transparency: bool = True
    ) -> None:
        Widget.__init__(self, parent)
        AbstractActionObject.__init__(self)
        self.name = name
        self.size = size if size else Size(1, 1)
        self.index = index
        self.pattern_table = ptn_tbl
        self.palette_set = pal_set
        self.tsa_offset = tsa_offset
        self._tsa_data = None
        self.transparency = transparency

        self._initialize_internal_observers()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.parent}, {self.name}, {self.index}, {self.pattern_table}, " \
               f"{self.palette_set}, {self.tsa_offset})"

    @property
    def size(self) -> Size:
        """The size of the block in units of 16 pixels"""
        return self._size

    @size.setter
    def size(self, size: Size) -> None:
        self._size = size
        self.size_update_action(self._size)

    @property
    def tsa_data(self) -> bytearray:
        """Find the tsa data from a given offset"""
        if not self._tsa_data:
            return ROM().bulk_read(TSA_TABLE_SIZE, (self.tsa_offset * TSA_TABLE_INTERVAL) + 0x10)
        else:
            return self._tsa_data

    @property
    def tsa_offset(self) -> int:
        """The offset in banks to the current tsa"""
        return self._tsa_offset

    @tsa_offset.setter
    def tsa_offset(self, offset: int) -> None:
        self._tsa_offset = offset
        self.refresh_event_action()

    @property
    def pattern_table(self) -> PatternTableHandler:
        """The pattern table for the tiles"""
        return self._pattern_table

    @pattern_table.setter
    def pattern_table(self, pattern_table: PatternTableHandler) -> None:
        self._pattern_table = pattern_table
        self.refresh_event_action()

    @property
    def palette_set(self) -> PaletteSet:
        """The palette currently used by the tsa"""
        return self._palette_set

    @palette_set.setter
    def palette_set(self, palette_set: PaletteSet) -> None:
        self._palette_set = palette_set
        self.refresh_event_action()

    @property
    def transparency(self) -> bool:
        """Determines if the blocks will be transparent"""
        return self._transparency

    @transparency.setter
    def transparency(self, transparency: bool) -> None:
        self._transparency = transparency
        self.refresh_event_action()

    def get_actions(self) -> List[Action]:
        """Gets the actions for the object"""
        return [
            Action("refresh_event", ObservableDecorator(lambda *_: self.update())),
            Action("size_update", ObservableDecorator(lambda size: size))
        ]

    def _initialize_internal_observers(self) -> None:
        """Initializes internal observers for special events"""
        self.size_update_action.observer.attach_observer(self.refresh_event_action)

    def sizeHint(self):
        """The ideal size of the widget"""
        return QSize(MetaBlock.image_length * self.size.width, MetaBlock.image_height * self.size.height)

    def paintEvent(self, event: QPaintEvent) -> None:
        """Paints the widget"""
        painter = QPainter(self)

        block = MetaBlock.from_rom(self.index, self.palette_set, self.pattern_table, self.tsa_data)
        block.draw(
            painter,
            Position(0, 0),
            Size(MetaBlock.image_length * self.size.width, MetaBlock.image_height * self.size.width),
            transparent=self.transparency
        )

        super().paintEvent(event)
