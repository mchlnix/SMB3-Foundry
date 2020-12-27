from copy import copy
from typing import Optional, List

from PySide2.QtWidgets import QWidget, QHBoxLayout

from foundry.core.Action.AbstractActionObject import AbstractActionObject
from foundry.core.Action.Action import Action
from foundry.core.Observables.ObservableDecorator import ObservableDecorator
from foundry.game.gfx.Palette import PaletteSet, Palette, Color
from foundry.gui.Custom.Palette.PaletteEditor import PaletteEditor
from foundry.gui.QCore.palette import DEFAULT_PALETTE_SET
from foundry.gui.QWidget import Widget


class PaletteSetEditor(Widget, AbstractActionObject):
    """A widget to help with editing a palette set"""
    palette_set_changed_action: Action  # Updated whenever the palette_set is changed

    def __init__(self, parent: Optional[QWidget], palette: Optional[PaletteSet] = DEFAULT_PALETTE_SET) -> None:
        Widget.__init__(self, parent)
        AbstractActionObject.__init__(self)
        self.parent = parent
        self.palette_set = copy(palette)

        self._set_up_layout()
        self._initialize_internal_observers()

    def _initialize_internal_observers(self) -> None:
        """Initializes internal observers for special events"""
        name = self.__class__.__name__

        def set_palette_closure(idx: int):
            """Returns a function that returns that sets a palette by palette index"""
            def set_palette(pal: Palette):
                """Sets a palette set by index"""
                return self._set_palette_set_color(idx, pal)
            return set_palette

        self.background_button.color_change_action.observer.attach_observer(
            lambda color: self._set_background_color(color), name=f"{name} Set Background Color"
        )
        for index, palette in enumerate(self.palette_editors):
            palette.palette_changed_action.observer.attach_observer(
                set_palette_closure(index), name=f"{name} Set Palette"
            )

    def _set_up_layout(self) -> None:
        """Returns the widgets layout"""
        from foundry.gui.Custom.Palette.NESPaletteSelector import ColorPickerButton
        self.palette_editors = []

        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)

        self.background_button = ColorPickerButton.as_tiny(self, self.palette_set.background_color)
        hbox.addWidget(self.background_button)
        for idx in range(4):
            editor = PaletteEditor(self, self.palette_set[idx])
            self.palette_editors.append(editor)
            hbox.addWidget(editor)

        self.setLayout(hbox)

    def _push_palette_set(self) -> None:
        """Forces an update to the entire palette set"""
        for idx, palette in enumerate(self.palette_editors):
            palette._palette = self.palette_set[idx]
            palette._push_palette_to_buttons()

    def _set_palette_set_color(self, pal_idx: int, palette: Palette) -> None:
        self.palette_set[pal_idx] = copy(palette)
        self.palette_set_changed_action.observer(copy(self.palette_set))

    def _set_background_color(self, color: Color):
        self.palette_set.background_color = color
        self.palette_set_changed_action.observer(copy(self.palette_set))

    def get_actions(self) -> List[Action]:
        """Gets the actions for the object"""
        return [
            Action("palette_set_changed", ObservableDecorator(lambda palette_set: palette_set, "Palette Set Updated")),
        ]