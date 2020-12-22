

from typing import Optional

from PySide2.QtWidgets import QWidget

from foundry.core.Action.AbstractActionObject import AbstractActionObject

from foundry.gui.QWidget import Widget

from foundry.game.gfx.PatternTableHandler import PatternTableHandler
from foundry.game.gfx.Palette import PaletteSet

from foundry.core.geometry.Size.Size import Size

from .BlockWidget import BlockWidget
from .BlockInjector import BlockInjector


class BlockInjection(BlockWidget):
    """BlockWidget that allows for references to block data"""

    def __init__(
            self,
            parent: Optional[QWidget],
            name: str,
            reference: BlockInjector,
            index: int
    ) -> None:
        Widget.__init__(self, parent)
        AbstractActionObject.__init__(self)
        self.name = name
        self.reference = reference
        self.index = index

        self._initialize_internal_observers()

    @property
    def size(self) -> Size:
        """The size of the block in units of 16 pixels"""
        return self.reference.size

    @size.setter
    def size(self, size: Size) -> None:
        self.reference.size = size
        self.size_update_action(self._size)

    @property
    def tsa_data(self) -> bytearray:
        """Find the tsa data from a given offset"""
        return self.reference.tsa_data

    @property
    def tsa_offset(self) -> int:
        """The offset in banks to the current tsa"""
        return 0

    @tsa_offset.setter
    def tsa_offset(self, offset: int) -> None:
        """Handled by reference"""

    @property
    def pattern_table(self) -> PatternTableHandler:
        """The pattern table for the tiles"""
        return self.reference.pattern_table

    @pattern_table.setter
    def pattern_table(self, pattern_table: PatternTableHandler) -> None:
        self.reference.pattern_table = pattern_table
        self.refresh_event_action()

    @property
    def palette_set(self) -> PaletteSet:
        """The palette currently used by the tsa"""
        return self.reference.palette_set

    @palette_set.setter
    def palette_set(self, palette_set: PaletteSet) -> None:
        self.reference.palette_set = palette_set
        self.refresh_event_action()

    @property
    def transparency(self) -> bool:
        """Determines if the blocks will be transparent"""
        return self.reference.transparency

    @transparency.setter
    def transparency(self, transparency: bool) -> None:
        self.reference.transparency = transparency
        self.refresh_event_action()
