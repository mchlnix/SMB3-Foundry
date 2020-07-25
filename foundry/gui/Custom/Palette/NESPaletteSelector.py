"""
NESPaletteSelector
"""

from typing import Optional, Callable
from PySide2.QtWidgets import QVBoxLayout, QWidget, QSizePolicy

from foundry.gui.QDialog import Dialog
from foundry.gui.Custom.Palette import ColorPicker
from foundry.gui.QToolButton import ColoredToolButton
from foundry.game.gfx.Palette import Color, PaletteController
from foundry.decorators.Observer import Observed


_palette_controller = PaletteController()


class ColorPickerButton(ColoredToolButton):
    def __init__(self, parent: Optional[QWidget], color: Color, return_call=None):
        super().__init__(parent, color)
        self.action = Observed(lambda *_: self.color if self._return_call is None else self._return_call)
        self._action.attach_observer(self.call_pop_up)
        self._return_call = return_call

    def add_observer(self, observer: Callable) -> None:
        """Adds an observer to the value"""
        self.action.attach_observer(observer)

    def call_pop_up(self, *_):
        """Calls on a pop up to select a new color"""
        ColorPickerPopup(self, action=lambda value: self.on_pop_up_finish(_palette_controller.colors[value])).exec_()

    def on_pop_up_finish(self, value: Color):
        """Called when the pop up finishes"""
        self.color = value
        self.action()


class ColorPickerPopup(Dialog):
    """Allows you to pick a custom color and returns the value"""

    def __init__(self, parent, title="Select a Color", action: Optional[Callable] = None) -> None:
        super().__init__(parent, title)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        layout = QVBoxLayout(self)
        self.color_picker = ColorPicker(self)
        self.color_picker.add_observer(lambda *_: self.accept())
        if action is not None:
            self.color_picker.add_observer(lambda result: action(result))
        layout.addWidget(self.color_picker)

        self.setLayout(layout)

