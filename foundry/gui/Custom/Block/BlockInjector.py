

from typing import Optional, List

from foundry.game.gfx.PatternTableHandler import PatternTableHandler
from foundry.game.gfx.Palette import PaletteSet

from foundry.core.Action.Action import Action
from foundry.core.Action.AbstractActionObject import AbstractActionObject
from foundry.core.Observables.ObservableDecorator import ObservableDecorator
from foundry.core.geometry.Size.Size import Size


class BlockInjector(AbstractActionObject):
    """The injector for references to the BlockInjector"""
    update_event_action: Action  # Used to notify when any attribute is updated
    size_update_action: Action  # Updates with size

    def __init__(
            self,
            size: Optional[Size],
            ptn_tbl: PatternTableHandler,
            pal_set: PaletteSet,
            tsa_data: bytearray,
            transparency: bool = True
    ):
        super().__init__()
        self._size = size
        self._pattern_table = ptn_tbl
        self._palette_set = pal_set
        self._tsa_data = tsa_data
        self._transparency = transparency

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.size}, {self.pattern_table}, {self.palette_set}, {self.tsa_data}, " \
               f"{self.transparency})"

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
        return self._tsa_data

    @tsa_data.setter
    def tsa_data(self, data: bytearray) -> None:
        self._tsa_data = data
        self.update_event_action()

    @property
    def pattern_table(self) -> PatternTableHandler:
        """The pattern table for the tiles"""
        return self._pattern_table

    @pattern_table.setter
    def pattern_table(self, pattern_table: PatternTableHandler) -> None:
        self._pattern_table = pattern_table
        self.update_event_action()

    @property
    def palette_set(self) -> PaletteSet:
        """The palette currently used by the tsa"""
        return self._palette_set

    @palette_set.setter
    def palette_set(self, palette_set: PaletteSet) -> None:
        self._palette_set = palette_set
        self.update_event_action()

    @property
    def transparency(self) -> bool:
        """Determines if the blocks will be transparent"""
        return self._transparency

    @transparency.setter
    def transparency(self, transparency: bool) -> None:
        self._transparency = transparency
        self.update_event_action()

    def get_actions(self) -> List[Action]:
        """Gets the actions for the object"""
        return [
            Action("update_event", ObservableDecorator(lambda *_: True)),
            Action("size_update", ObservableDecorator(lambda size: size))
        ]
