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

from foundry.game.gfx.PatternTableHandler import PatternTableHandler
from foundry.game.gfx.Palette import PaletteSet
from foundry.game.gfx.drawable.Block import Block as MetaBlock

from foundry.core.Observables.ObservableDecorator import ObservableDecorator
from foundry.core.geometry.Position.Position import Position
from foundry.core.geometry.Size.Size import Size

from .AbstractBlock import AbstractBlock


class BlockWidget(Widget, AbstractActionObject):
    """A class for keeping track of a Block"""
    refresh_event_action: Action  # Used internally for redrawing the widget
    block_update_action: Action  # Updates whenever something that defines the block changes
    size_update_action: Action  # Updates when the size updates

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

        self._initialize_internal_observers()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.parent}, {self.name}, {self.index}, {self.pattern_table}, " \
               f"{self.palette_set}, {self.tsa_offset})"

    @property
    def size(self) -> Size:
        """The size of the block in units of 16 pixels"""
        return self.block.size

    @size.setter
    def size(self, size: Size) -> None:
        self.block.size = size
        self.size_update_action(self._size)

    @property
    def tsa_data(self) -> bytearray:
        """Find the tsa data from a given offset"""
        return self.block.tsa_data

    @tsa_data.setter
    def tsa_data(self, tsa_data: bytearray) -> None:
        self.block.tsa_data = tsa_data
        self.refresh_event_action()

    @property
    def pattern_table(self) -> PatternTableHandler:
        """The pattern table for the tiles"""
        return self.block.pattern_table

    @pattern_table.setter
    def pattern_table(self, pattern_table: PatternTableHandler) -> None:
        self.block.pattern_table = pattern_table
        self.refresh_event_action()

    @property
    def palette_set(self) -> PaletteSet:
        """The palette currently used by the tsa"""
        return self.block.palette_set

    @palette_set.setter
    def palette_set(self, palette_set: PaletteSet) -> None:
        self.block.palette_set = palette_set
        self.refresh_event_action()

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
        self.block.draw(painter, Position(0, 0))
        super().paintEvent(event)
