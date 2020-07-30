

from typing import Optional, List
from PySide2.QtWidgets import QWidget, QGridLayout
from PySide2.QtGui import Qt

from foundry.gui.QCore.Action import Action, AbstractActionObject
from foundry.gui.QCore.palette import DEFAULT_PALETTE_SET
from foundry.gui.QCore.pattern_table import PATTERN_TBL_DEFAULT
from foundry.gui.QCore import MARGIN_TIGHT

from foundry.game.gfx.objects.objects.LevelObjectDefinition import SpriteGraphic
from foundry.game.gfx.PatternTableHandler import PatternTableHandler
from foundry.game.gfx.Palette import PaletteSet

from foundry.gui.QWidget import Widget
from foundry.gui.Custom.Sprite import SpriteDisplayerTracker

from foundry.core.Observable import Observable


class SpriteSelector(Widget, AbstractActionObject):
    """A class for keeping track of a SpriteGraphic"""
    def __init__(
            self,
            parent: Optional[QWidget],
            pattern_table: Optional[PatternTableHandler] = None,
            palette: Optional[PaletteSet] = DEFAULT_PALETTE_SET,
            palette_index: int = 0
    ) -> None:
        Widget.__init__(self, parent)
        AbstractActionObject.__init__(self)
        if pattern_table is None:
            pattern_table = PatternTableHandler(PATTERN_TBL_DEFAULT)
        self._pattern_table = pattern_table
        self._palette = palette
        self._palette_index = palette_index

        self._set_up_layout()

    def _set_up_layout(self) -> None:
        """Returns the widgets layout"""
        self.sprites = []
        grid_layout = QGridLayout()
        grid_layout.setSpacing(MARGIN_TIGHT)
        grid_layout.setDefaultPositioning(0x10, Qt.Horizontal)
        for idx in range(1, 0x200, 2):
            sprite = SpriteDisplayerTracker(
                self, SpriteGraphic(idx), self.palette_index, self.palette, self.pattern_table
            )
            self.sprites.append(sprite)
            grid_layout.addWidget(sprite)

        self.setLayout(grid_layout)

    def get_actions(self) -> List[Action]:
        """Gets the actions for the object"""
        return [
            Action("sprite_selected", Observable(lambda index: index)),
        ]

    @property
    def pattern_table(self) -> PatternTableHandler:
        """Displays the current page of graphics"""
        return self._pattern_table

    @pattern_table.setter
    def pattern_table(self, pattern_table: PatternTableHandler) -> None:
        self._pattern_table = pattern_table

    @property
    def palette(self) -> PaletteSet:
        """Determines the colors of the sprites displayed"""
        return self._palette

    @palette.setter
    def palette(self, palette: PaletteSet) -> None:
        self._palette = palette

    @property
    def palette_index(self) -> int:
        """The index of the palette"""
        return self._palette_index

    @palette_index.setter
    def palette_index(self, index: int) -> None:
        self._palette_index = index
