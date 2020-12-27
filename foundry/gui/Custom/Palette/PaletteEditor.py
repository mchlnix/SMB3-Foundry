from copy import copy
from typing import Optional, List

from PySide2.QtWidgets import QWidget, QHBoxLayout

from foundry.gui.Custom.Palette.NESPaletteSelector import ColorPickerButton
from foundry.core.Action.AbstractActionObject import AbstractActionObject
from foundry.core.Action.Action import Action
from foundry.core.Observables.ObservableDecorator import ObservableDecorator
from foundry.game.gfx.Palette import Palette, Color
from foundry.gui.QCore.palette import DEFAULT_PALETTE
from foundry.gui.QWidget import Widget


class PaletteEditor(Widget, AbstractActionObject):
    """A widget to help edit a single palette"""
    palette_changed_action: Action  # Updates whenever the palette changes

    def __init__(self, parent: Optional[QWidget], palette: Optional[Palette] = DEFAULT_PALETTE) -> None:
        Widget.__init__(self, parent)
        AbstractActionObject.__init__(self)
        self.parent = parent
        self._palette = copy(palette)

        self._set_up_layout()
        self._initialize_internal_observers()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.parent}, {self.palette})"

    def _set_up_layout(self) -> None:
        """Returns the widgets layout"""
        self.buttons = []
        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(0)
        for idx in range(3):
            button = ColorPickerButton.as_tiny(self, self.palette[idx + 1])
            self.buttons.append(button)
            hbox.addWidget(button)
        self.setLayout(hbox)

    def _initialize_internal_observers(self) -> None:
        """Initializes internal observers for special events"""
        name = self.__class__.__name__

        def set_palette_color_closure(index):
            """Returns a function that sets a palette color by index"""
            def set_palette_color(color: Color):
                """Sets a palette color by index"""
                self.palette[index + 1] = color
                self.palette_changed_action.observer(copy(self.palette))
            return set_palette_color

        def set_button_color_closure(btn: ColorPickerButton, index: int):
            """A closure for setting a button's color"""
            def set_button_colors(*_):
                """Sets a button's colors"""
                btn.color = self.palette[index + 1]
            return set_button_colors

        for idx, button in enumerate(self.buttons):
            self.palette_changed_action.observer.attach_observer(
                set_button_color_closure(button, idx), name=f"{name} Set Button Colors"
            )
            button.color_change_action.observer.attach_observer(
                set_palette_color_closure(idx), name=f"{name} Set Palette Color"
            )

    def _push_palette_to_buttons(self) -> None:
        """Pushes the palette onto the palette buttons"""
        for idx, button in enumerate(self.buttons):
            button._set_color(self.palette[idx + 1])  # pushes the color to the button without updating the palette

    def get_actions(self) -> List[Action]:
        """Gets the actions for the object"""
        return [
            Action("palette_changed", ObservableDecorator(lambda palette: palette, "Palette Updated")),
        ]

    @property
    def palette(self) -> Palette:
        """The palette we are controlling"""
        return self._palette

    @palette.setter
    def palette(self, palette: Palette) -> None:
        if palette != self.palette:
            self._palette = palette
            self.palette_changed_action(copy(palette))
