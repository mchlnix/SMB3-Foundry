

from typing import Optional, Callable, Tuple
from PySide2.QtWidgets import QGridLayout, QWidget, QSizePolicy, QLayout, QHBoxLayout
from PySide2.QtGui import Qt

from foundry.gui.QCore import MARGIN_TIGHT
from foundry.gui.QToolButton import ColoredToolButton
from foundry.game.gfx.Palette import PaletteController, PaletteSet, Palette, Color
from foundry.decorators.Observer import Observed


_palette_controller = PaletteController()
_default_color = Color(0, 0, 0)
_default_palette = Palette(_default_color, _default_color, _default_color, _default_color)
_default_palette_set = PaletteSet(_default_palette, _default_palette, _default_palette, _default_palette)



class ColorPicker(QWidget):
    """A widget to help with picking a NES color"""
    def __init__(self, parent: Optional[QWidget]) -> None:
        super().__init__(parent)
        self.parent = parent
        self.action = Observed(lambda color: color)

        self.buttons = []
        grid_layout = QGridLayout()
        grid_layout.setSizeConstraint(QLayout.SetFixedSize)
        grid_layout.setSpacing(MARGIN_TIGHT)
        grid_layout.setDefaultPositioning(0x10, Qt.Horizontal)
        for idx in range(0x40):
            button = ColoredToolButton.as_tiny(self, _palette_controller.colors[idx], idx)
            button.add_observer(lambda color: self.action(color))
            self.buttons.append(button)
            grid_layout.addWidget(button, row=idx % 0x10, column=idx // 0x10)

        self.setLayout(grid_layout)

    def add_observer(self, observer: Callable) -> None:
        """Adds an observer to the value"""
        self.action.attach_observer(observer)




