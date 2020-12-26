

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
from foundry.gui.Custom.Block.AbstractBlock import AbstractBlock
from foundry.gui.QSpinner.HexSpinner import HexSpinner
from foundry.gui.QWidget import Widget
from foundry.gui.Custom.BlockPattern.BlockPattern import BlockPattern


class BlockEditor(Widget, AbstractActionObject):
    """A spinner in charge of the keeping the position"""
    refresh_event_action: Action  # Used internally for redrawing the widget
    size_update_action: Action  # Updates when the size updates
    values_changed_action: Action  # When the spinners change values
    text_changed_action: Action  # When the spinners change text
    block_changed_action: Action  # When the block changes the tsa

    def __init__(self, parent: Optional[QWidget], block: AbstractBlock) -> None:
        Widget.__init__(self, parent)
        AbstractActionObject.__init__(self)

        self.block = block
        self._block_pattern = BlockPattern.from_tsa_data(self.block.index, self.block.tsa_data)

        self._set_up_layout()
        self._initialize_internal_observers()

        self.index = self.block.index  # Update the spinners

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.parent}, {self.spinners})"

    @property
    def block_pattern(self) -> BlockPattern:
        """The pattern of the current block"""
        return self._block_pattern

    @block_pattern.setter
    def block_pattern(self, pattern: BlockPattern) -> None:
        self._block_pattern = pattern
        self._push_block_update()
        self.block_changed_action(self.tsa_data)

    @property
    def index(self) -> int:
        """The index the block is in for the tsa"""
        return self.block.index

    @index.setter
    def index(self, index: int) -> None:
        self.block.index = index
        self.block_pattern = BlockPattern.from_tsa_data(self.block.index, self.block.tsa_data)

    @property
    def tsa_data(self) -> bytearray:
        """"The pattern table of the block"""
        return self.block.tsa_data

    @tsa_data.setter
    def tsa_data(self, tsa_data: bytearray) -> None:
        self.block.tsa_data = tsa_data

    @property
    def size(self) -> Size:
        """The size of the block in units of 16 pixels"""
        return self.block.size

    @size.setter
    def size(self, size: Size) -> None:
        self.block.size = size

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
        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)

        top_left_spinner = HexSpinner(self, maximum=0xFF)
        grid.addWidget(top_left_spinner, 0, 0)

        top_right_spinner = HexSpinner(self, maximum=0xFF)
        grid.addWidget(top_right_spinner, 0, 2)

        self.block = BlockWidget(self, "Block", self.block)
        grid.addWidget(self.block, 0, 1, 0, 1, Qt.AlignCenter)

        bottom_left_spinner = HexSpinner(self, maximum=0xFF)
        grid.addWidget(bottom_left_spinner, 1, 0)

        bottom_right_spinner = HexSpinner(self, maximum=0xFF)
        grid.addWidget(bottom_right_spinner, 1, 2)

        self.spinners = [top_left_spinner, bottom_left_spinner, top_right_spinner, bottom_right_spinner]
        self.setLayout(grid)

    def _initialize_internal_observers(self) -> None:
        """Initializes internal observers for special events"""
        def update_block_pattern_closure(idx):
            """Updates the block pattern"""
            def update_block_pattern(value):
                """The inner function"""
                if value != self.block_pattern[idx]:
                    self.block_pattern[idx] = value
                    self._push_block_update()
            return update_block_pattern

        for idx, spinner in enumerate(self.spinners):
            spinner.value_changed_action.observer.attach_observer(update_block_pattern_closure(idx))
        self.block.refresh_event_action.observer.attach_observer(lambda *_: self.refresh_event_action())
        self.block.size_update_action.observer.attach_observer(lambda size: self.size_update_action(size))

    def _push_block_update(self) -> None:
        """Pushes an update to the block"""
        for idx, spinner in enumerate(self.spinners):
            self.tsa_data[(idx * 256) + self.index] = self.block_pattern[idx]
            if spinner.value() != self.block_pattern[idx]:
                spinner.setValue(self.block_pattern[idx])
        self.refresh_event_action()

    def get_actions(self) -> List[Action]:
        """Gets the actions for the object"""
        name = self.__class__.__name__
        return [
            Action("refresh_event", ObservableDecorator(lambda *_: self.update(), f"{name} Refreshed")),
            Action("size_update", ObservableDecorator(lambda size: size, f"{name} Size Updated")),
            Action("values_changed", ObservableDecorator(lambda palette_set: palette_set, f"{name} Value Updated")),
            Action("text_changed", ObservableDecorator(lambda palette_set: palette_set, f"{name} Text Updated")),
            Action("block_changed", ObservableDecorator(lambda tsa_data: tsa_data, f"{name} Block Updated"))
        ]


