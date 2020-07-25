

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


class PaletteSetEditor(QWidget):
    """A widget to help with editing a palette set"""

    def __init__(self, parent: Optional[QWidget], palette: Optional[PaletteSet] = _default_palette_set) -> None:
        from foundry.gui.Custom.Palette.NESPaletteSelector import ColorPickerButton
        super().__init__(parent)
        self.parent = parent
        self.palette = palette
        self.action = Observed(lambda *_: self.palette)
        self.add_observer(lambda *_: print(self.palette))

        self.palette_editors = []
        hbox = QHBoxLayout()
        hbox.setSizeConstraint(QLayout.SetFixedSize)
        hbox.setSpacing(MARGIN_TIGHT)

        self.background_button = ColorPickerButton.as_tiny(self, self.palette[0][0])
        self.background_button.add_observer(lambda *_: self._set_palette_set_color(0, 0, self.background_button.color))
        hbox.addWidget(self.background_button)

        for idx in range(4):
            editor = PaletteEditor(self, self.palette[idx])
            editor.add_observer(lambda pal: self._set_palette_set_palette(idx, pal))
            self.palette_editors.append(editor)
            hbox.addWidget(editor)
        self.setLayout(hbox)

    def _set_palette_set_color(self, pal_idx, idx, color) -> None:
        p_set = list(self.palette)
        p = list(p_set[pal_idx])
        p[idx] = color
        p_set[pal_idx] = Palette(p[0], p[1], p[2], p[3])
        self.palette = PaletteSet(p_set[0], p_set[1], p_set[2], p_set[3])
        self.action()

    def _set_palette_set_palette(self, pal_idx: int, palette: Palette):
        p_set = list(self.palette)
        p_set[pal_idx] = palette
        self.palette = PaletteSet(p_set[0], p_set[1], p_set[2], p_set[3])

    def add_observer(self, observer: Callable) -> None:
        """Adds an observer to the value"""
        self.action.attach_observer(observer)


class PaletteEditor(QWidget):
    """A widget to help edit a single palette"""
    def __init__(self, parent: Optional[QWidget], palette: Optional[Palette] = _default_palette) -> None:
        from foundry.gui.Custom.Palette.NESPaletteSelector import ColorPickerButton
        super().__init__(parent)
        self.parent = parent
        self.palette = palette
        self.action = Observed(lambda *_: self.palette)

        self.buttons = []
        hbox = QHBoxLayout()
        hbox.setSizeConstraint(QLayout.SetFixedSize)
        hbox.setSpacing(0)
        for idx in range(3):
            button = ColorPickerButton.as_tiny(self, _palette_controller.colors[idx], idx)
            button.add_observer(lambda idx: self._set_palette_color(idx, self.buttons[idx].color))
            self.buttons.append(button)
            hbox.addWidget(button)
        self.setLayout(hbox)

    def _set_palette_color(self, idx, color) -> None:
        p = list(self.palette)
        p[idx] = color
        self.palette = Palette(p[0], p[1], p[2], p[3])
        self.action()

    def add_observer(self, observer: Callable) -> None:
        """Adds an observer to the value"""
        self.action.attach_observer(observer)


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




