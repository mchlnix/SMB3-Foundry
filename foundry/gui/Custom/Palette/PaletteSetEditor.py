from copy import copy
from typing import Optional, List

from PySide2.QtWidgets import QWidget, QHBoxLayout

from foundry.core.Action.AbstractActionObject import AbstractActionObject
from foundry.core.Action.Action import Action
from foundry.core.Observables.ObservableDecorator import ObservableDecorator
from foundry.game.gfx.Palette import PaletteController, PaletteSet, Palette, Color
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
        self._palette_set = copy(palette)

        self._set_up_layout()
        self._initialize_internal_observers()

    def _initialize_internal_observers(self) -> None:
        """Initializes internal observers for special events"""
        name = self.__class__.__name__

        def set_palette_closure(idx: int):
            """Returns a function that returns that sets a palette by palette index"""
            def set_palette(pal: Palette):
                """Sets a palette set by index"""
                old_pal = copy(self.palette_set)
                old_pal[idx] = copy(pal)
                self.palette_set = old_pal
            return set_palette

        def set_palettes_palette_closure(idx: int):
            """Sets the palette's palette whenever the palette set changes"""
            def set_palettes_palette(pal: PaletteSet):
                """Set the palette's palette"""
                self.palette_editors[idx].palette = pal[idx]
            return set_palettes_palette

        def set_background_color(color: Color):
            """Sets a background color for a palette set"""
            self.palette_set.background_color = color
            self.palette_set_changed_action.observer(copy(self.palette_set))

        self.background_button.color_change_action.observer.attach_observer(
            lambda color: set_background_color(color), name=f"{name} Set Background Color"
        )
        for index, palette in enumerate(self.palette_editors):
            palette.palette_changed_action.observer.attach_observer(
                set_palette_closure(index), name=f"{name} Set Palette"
            )
            self.palette_set_changed_action.observer.attach_observer(
                set_palettes_palette_closure(index), name=f"{name} Set Palette"
            )

        self.palette_set_changed_action.observer.attach_observer(
            lambda palette_set: setattr(self.background_button, "color", palette_set.background_color)
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

    def get_actions(self) -> List[Action]:
        """Gets the actions for the object"""
        return [
            Action("palette_set_changed", ObservableDecorator(lambda palette_set: palette_set, "Palette Set Updated")),
        ]

    @property
    def palette_set(self) -> PaletteSet:
        """The PaletteSet used"""
        return copy(self._palette_set)

    @palette_set.setter
    def palette_set(self, palette_set: PaletteSet) -> None:
        if palette_set != self.palette_set:
            self._palette_set = copy(palette_set)
            self.palette_set_changed_action.observer(copy(self.palette_set))
