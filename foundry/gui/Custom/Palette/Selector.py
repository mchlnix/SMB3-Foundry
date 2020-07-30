"""
PaletteSelector
"""

from typing import Optional, List
from PySide2.QtWidgets import QWidget, QHBoxLayout
from PySide2.QtGui import Qt

from . import PaletteEditor
from foundry.gui.QSpinner import Spinner
from foundry.gui.QCore.palette import DEFAULT_PALETTE_SET
from foundry.game.gfx.Palette import PaletteSet, Palette
from foundry.core.Observable import Observed
from foundry.gui.QWidget import Widget
from foundry.gui.QCore.Action import Action, AbstractActionObject


class PaletteSelector(Widget, AbstractActionObject):
    """A widget to help edit a single palette"""
    def __init__(
            self, parent: Optional[QWidget], index: int, palette: Optional[PaletteSet] = DEFAULT_PALETTE_SET
    ) -> None:
        Widget.__init__(self, parent)
        AbstractActionObject.__init__(self)
        self.parent = parent
        self._palette_set = palette
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
        self.palette_editor.palette_changed_action.observer.attach(
            lambda palette: setattr(self, "palette", palette)
        )
        self.spinner.value_changed_action.observer.attach(
            lambda index: setattr(self, "index", index)
        )

    def get_actions(self) -> List[Action]:
        """Gets the actions for the object"""
        return [
            Action("palette_set_changed", Observed(lambda palette_set: palette_set)),
            Action("palette_changed", Observed(lambda palette: palette)),
        ]

    @property
    def palette_set(self) -> PaletteSet:
        """The palette set we are controlling"""
        return self._palette_set

    @palette_set.setter
    def palette_set(self, palette_set: PaletteSet) -> None:
        self._palette_set = palette_set
        self._update_palette()
        self.palette_set_changed_action.observer(palette_set)

    @property
    def palette(self) -> Palette:
        """The palette set currently selected"""
        return self.palette_set[self.index]

    @palette.setter
    def palette(self, palette: Palette) -> None:
        self.palette_set[self.index] = palette
        self._update_palette()
        self.palette_changed_action.observer(palette)

    def _update_palette(self):
        self.palette_editor._set_palette(self.palette)  # update the palette without providing an update

    @property
    def index(self) -> int:
        """The index into the palette set"""
        return self._index

    @index.setter
    def index(self, index: int) -> None:
        self._index = index
        self._update_palette()
