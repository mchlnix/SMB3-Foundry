"""
PaletteSelector
"""

from copy import copy
from typing import Optional, List
from PySide2.QtWidgets import QWidget, QHBoxLayout
from PySide2.QtGui import Qt

from .PaletteEditor import PaletteEditor
from foundry.gui.QSpinner import Spinner
from foundry.gui.QCore.palette import DEFAULT_PALETTE_SET
from foundry.game.gfx.Palette import PaletteSet, Palette
from foundry.core.Observables.ObservableDecorator import ObservableDecorator
from foundry.gui.QWidget import Widget
from foundry.core.Action.Action import Action
from foundry.core.Action.AbstractActionObject import AbstractActionObject


class PaletteSelector(Widget, AbstractActionObject):
    """A widget to help edit a single palette"""

    palette_set_changed_action: Action  # Updated whenever the palette_set is changed
    palette_changed_action: Action  # Updated whenever the palette is changed
    index_changed_action: Action  # Updated whenever the index is changed

    def __init__(
            self, parent: Optional[QWidget], index: int, palette: Optional[PaletteSet] = DEFAULT_PALETTE_SET
    ) -> None:
        Widget.__init__(self, parent)
        AbstractActionObject.__init__(self)
        self.parent = parent
        self._palette_set = copy(palette)
        self._index = index

        self._set_up_layout()
        self._initialize_internal_observers()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.parent}, {self.checkboxes})"

    def _set_up_layout(self) -> None:
        """Returns the widgets layout"""
        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setAlignment(Qt.AlignVCenter)

        self.palette_editor = PaletteEditor(self, self.palette)
        hbox.addWidget(self.palette_editor)

        self.spinner = Spinner(self, maximum=3)
        hbox.addWidget(self.spinner)

        self.setLayout(hbox)

    def _initialize_internal_observers(self) -> None:
        """Initializes internal observers for special events"""
        name = self.__class__.__name__
        self.palette_editor.palette_changed_action.observer.attach_observer(
            lambda palette: setattr(self, "palette", palette),
            name=f"{name} Set Palette"
        )
        self.spinner.value_changed_action.observer.attach_observer(
            lambda index: setattr(self, "index", index),
            name=f"{name} Set Index"
        )

        self.palette_set_changed_action.observer.attach_observer(
            lambda *_: setattr(self.palette_editor, "palette", self.palette),
            name=f"{name} Set Palette"
        )
        self.index_changed_action.observer.attach_observer(
            lambda *_: setattr(self.palette_editor, "palette", self.palette),
            name=f"{name} Set Palette"
        )

    def get_actions(self) -> List[Action]:
        """Gets the actions for the object"""
        name = self.__class__.__name__
        return [
            Action("palette_set_changed", ObservableDecorator(
                lambda palette_set: palette_set, f"{name} Palette Set Updated"
            )),
            Action("palette_changed", ObservableDecorator(
                lambda palette: palette, f"{name} Palette Updated"
            )),
            Action("index_changed", ObservableDecorator(
                lambda index: index, f"{name} Index Updated"
            ))
        ]

    @property
    def palette_set(self) -> PaletteSet:
        """The palette set we are controlling"""
        return copy(self._palette_set)

    @palette_set.setter
    def palette_set(self, palette_set: PaletteSet) -> None:
        if palette_set != self.palette_set:
            self._palette_set = copy(palette_set)
            self.palette_set_changed_action.observer(copy(palette_set))

    @property
    def palette(self) -> Palette:
        """The palette set currently selected"""
        return copy(self.palette_set[self.index])

    @palette.setter
    def palette(self, palette: Palette) -> None:
        if palette != self.palette:
            self.palette_set[self.index] = copy(palette)
            self.palette_changed_action.observer(copy(palette))

    @property
    def index(self) -> int:
        """The index into the palette set"""
        return self._index

    @index.setter
    def index(self, index: int) -> None:
        if index != self.index:
            self._index = index
            self.index_changed_action(self.index)
