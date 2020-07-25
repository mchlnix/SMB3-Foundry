"""
NESPaletteSelector
"""

from typing import Optional, Callable
from PySide2.QtWidgets import QVBoxLayout, QWidget

from foundry.gui.QDialog import Dialog
from foundry.gui.Custom.Palette import ColorPicker
from foundry.gui.QToolButton import ColoredToolButton
from foundry.game.gfx.Palette import Color, PaletteController
from foundry.decorators.Observer import Observed


_palette_controller = PaletteController()

class ColorPickerPopup(Dialog):
    """Allows you to pick a custom color and returns the value"""

    def __init__(self, parent, title="Select a Color", action: Optional[Callable] = None) -> None:
        super().__init__(parent, title)

        layout = QVBoxLayout(self)
        self.color_picker = ColorPicker(self)
        self.color_picker.add_observer(lambda *_: self.accept())
        if action is not None:
            self.color_picker.add_observer(lambda result: action(result))
        layout.addWidget(self.color_picker)

        self.setLayout(layout)

