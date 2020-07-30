"""
NESPaletteSelector
"""

from typing import List, Optional, Callable, Union
from PySide2.QtWidgets import QVBoxLayout, QWidget

from foundry.gui.QDialog import Dialog
from foundry.gui.Custom.Palette import ColorPicker
from foundry.gui.QToolButton import ColoredToolButton
from foundry.game.gfx.Palette import Color, PaletteController
from foundry.core.Observables.ObservableDecorator import ObservableDecorator
from foundry.gui.QCore.Action import Action


_palette_controller = PaletteController()


class ColorPickerButton(ColoredToolButton):
    """A colored button that pops up a dialog whenever clicked"""
    def __init__(self, parent: Optional[QWidget], color: Union[int, Color]):
        if isinstance(color, int):
            color_index, color = color, _palette_controller.colors[color]
        else:
            color_index, color = _palette_controller.colors_inverse[color], color

        ColoredToolButton.__init__(self, parent, color)
        self._color_index = color_index

        self._initialize_internal_observers()

    def _initialize_internal_observers(self):
        """Initializes internal observers for special events"""
        self.clicked_action.observer.attach_observer(self.call_pop_up)

    def get_actions(self) -> List[Action]:
        """Gets the actions for the object"""
        return [
            Action.from_signal("clicked", self.clicked, False),
            Action.from_signal("pressed", self.pressed, False),
            Action.from_signal("released", self.released, False),
            Action("color_change", ObservableDecorator(lambda color: color)),
            Action("color_index_change", ObservableDecorator(lambda color_index: color_index)),
        ]

    def call_pop_up(self, *_):
        """Calls on a pop up to select a new color"""
        ColorPickerPopup(self, action=lambda value: self.pop_up_finished(value)).exec_()

    def pop_up_finished(self, value: int) -> None:
        """The method called on pop up finish"""
        self.color_index = value

    @property
    def color_index(self) -> int:
        """Returns the current color index of the button"""
        return self._color_index

    @color_index.setter
    def color_index(self, color_index: int) -> None:
        self._color_index = color_index
        self.color = _palette_controller.colors[color_index]

        self.color_index_change_action.observer(color_index)


class ColorPickerPopup(Dialog):
    """Allows you to pick a custom color and returns the value"""

    def __init__(self, parent, title="Select a Color", action: Optional[Callable] = None) -> None:
        Dialog.__init__(self, parent, title)

        self._set_up_layout()
        self._initialize_internal_observers(action)

    def _set_up_layout(self) -> None:
        """Returns the widgets layout"""
        layout = QVBoxLayout(self)
        self.color_picker = ColorPicker(self)
        layout.addWidget(self.color_picker)
        self.setLayout(layout)

    def _initialize_internal_observers(self, action) -> None:
        """Initializes internal observers for special events"""
        self.color_picker.color_index_selected_action.observer.attach_observer(lambda *_: self.accept())  # closes the dialog

        if action is not None:
            self.color_picker.color_index_selected_action.observer.attach_observer(lambda value: action(value))
