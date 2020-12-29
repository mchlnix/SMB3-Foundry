

from typing import Optional, Callable
from PySide2.QtWidgets import QVBoxLayout

from foundry.gui.QDialog import Dialog

from foundry.game.gfx.PatternTableHandler import PatternTableHandler
from foundry.game.gfx.Palette import Palette

from foundry.core.geometry.Size.Size import Size

from .TileSelector import TileSelector


class TileSelectorPopup(Dialog):
    """Allows you to pick a custom color and returns the value"""

    def __init__(
            self,
            parent,
            pattern_table: PatternTableHandler,
            palette: Palette,
            title="Select a Tile",
            action: Optional[Callable] = None,
            size: Size = None
    ) -> None:
        Dialog.__init__(self, parent, title)
        self.size = size
        self.pattern_table = pattern_table
        self.palette = palette

        self._set_up_layout()
        self._initialize_internal_observers(action)

    def _set_up_layout(self) -> None:
        """Returns the widgets layout"""
        layout = QVBoxLayout(self)
        self.tile_picker = TileSelector(self, self.size, self.pattern_table, self.palette)
        layout.addWidget(self.tile_picker)
        self.setLayout(layout)

    def _initialize_internal_observers(self, action) -> None:
        """Initializes internal observers for special events"""
        name = self.__class__.__name__
        self.tile_picker.single_clicked_action.observer.attach_observer(
            lambda *_: self.accept(), name=f"{name} Closed"
        )

        if action is not None:
            self.tile_picker.single_clicked_action.observer.attach_observer(
                lambda value: action(value), name=f"{name} Returned Tile to Action"
            )