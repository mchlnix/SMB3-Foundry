

from typing import Optional, List
from PySide2.QtWidgets import QWidget, QGridLayout
from PySide2.QtGui import Qt

from foundry.game.gfx.PatternTableHandler import PatternTableHandler
from foundry.game.gfx.Palette import PaletteSet

from foundry.core.Observables.ObservableDecorator import ObservableDecorator
from foundry.core.Action.Action import Action
from foundry.core.geometry.Size.Size import Size

from foundry.gui.QCore.Tracker import AbstractActionObject
from foundry.gui.Custom.Block.BlockWidget import BlockWidget
from foundry.gui.QSpinner.HexSpinner import HexSpinner
from foundry.gui.QWidget import Widget


class BlockEditor(Widget, AbstractActionObject):
    """A spinner in charge of the keeping the position"""
    refresh_event_action: Action  # Used internally for redrawing the widget
    size_update_action: Action  # Updates when the size updates
    values_changed_action: Action  # When the spinners change values
    text_changed_action: Action  # When the spinners change text

    def __init__(self, parent: Optional[QWidget], block: BlockWidget) -> None:
        Widget.__init__(self, parent)
        AbstractActionObject.__init__(self)

        self.block = block
        self._set_up_layout()
        self._initialize_internal_observers()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.parent}, {self.spinners})"

    @property
    def size(self) -> Size:
        """The size of the block in units of 16 pixels"""
        return self.block.size

    @size.setter
    def size(self, size: Size) -> None:
        self.block.size = size

    @property
    def tsa_data(self) -> bytearray:
        """Find the tsa data from a given offset"""
        return self.block.tsa_data

    @property
    def tsa_offset(self) -> int:
        """The offset in banks to the current tsa"""
        return self.block.tsa_offset

    @tsa_offset.setter
    def tsa_offset(self, offset: int) -> None:
        self.block.tsa_offset = offset

    @property
    def pattern_table(self) -> PatternTableHandler:
        """The pattern table for the tiles"""
        return self.block.pattern_table

    @pattern_table.setter
    def pattern_table(self, pattern_table: PatternTableHandler) -> None:
        self.block.pattern_table = pattern_table

    @property
    def palette_set(self) -> PaletteSet:
        """The palette currently used by the tsa"""
        return self.palette_set

    @palette_set.setter
    def palette_set(self, palette_set: PaletteSet) -> None:
        self.block.palette_set = palette_set

    @property
    def transparency(self) -> bool:
        """Determines if the blocks will be transparent"""
        return self.block.transparency

    @transparency.setter
    def transparency(self, transparency: bool) -> None:
        self.block.transparency = transparency

    def _set_up_layout(self) -> None:
        """Returns the widgets layout"""
        self.spinners = []
        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)

        top_left_spinner = HexSpinner(self, maximum=0xFF)
        grid.addWidget(top_left_spinner, 0, 0)

        top_right_spinner = HexSpinner(self, maximum=0xFF)
        grid.addWidget(top_right_spinner, 0, 2)

        grid.addWidget(self.block, 0, 1, 0, 1, Qt.AlignCenter)

        bottom_left_spinner = HexSpinner(self, maximum=0xFF)
        grid.addWidget(bottom_left_spinner, 1, 0)

        bottom_right_spinner = HexSpinner(self, maximum=0xFF)
        grid.addWidget(bottom_right_spinner, 1, 2)

        self.setLayout(grid)

    def _initialize_internal_observers(self) -> None:
        """Initializes internal observers for special events"""
        for spinner in self.spinners:
            spinner.value_changed_action.observer.attach_observer(lambda *_: self._update_changed_values())
            spinner.text_changed_action.observer.attach_observer(lambda *_: self._update_text_values())
        self.block.refresh_event_action.observer.attach_observer(lambda *_: self.refresh_event_action())
        self.block.size_update_action.observer.attach_observer(lambda size: self.size_update_action(size))

    def _update_changed_values(self):
        """Returns the changed values from the spinners"""
        self.values_changed_action.observer([spinner.value() for spinner in self.spinners])

    def _update_text_values(self):
        """Returns the changed text from the spinners"""
        self.text_changed_action.observer([spinner.text() for spinner in self.spinners])

    def get_actions(self) -> List[Action]:
        """Gets the actions for the object"""
        return [
            Action("refresh_event", ObservableDecorator(lambda *_: self.update())),
            Action("size_update", ObservableDecorator(lambda size: size)),
            Action("values_changed", ObservableDecorator(lambda palette_set: palette_set)),
            Action("text_changed", ObservableDecorator(lambda palette_set: palette_set)),
        ]


