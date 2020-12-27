

from typing import Optional, List
from PySide2.QtWidgets import QWidget, QGridLayout
from PySide2.QtGui import Qt

from foundry.game.gfx.PatternTableHandler import PatternTableHandler
from foundry.game.gfx.Palette import PaletteSet

from foundry.core.Observables.ObservableDecorator import ObservableDecorator
from foundry.core.Action.Action import Action
from foundry.core.geometry.Size.Size import Size

from foundry.gui.QCore.Tracker import AbstractActionObject
from foundry.gui.Custom.Block.BlockTileTrackableObject import BlockTileTrackableObject
from foundry.gui.Custom.Block.AbstractBlock import AbstractBlock
from foundry.gui.QSpinner.HexSpinner import HexSpinner
from foundry.gui.QWidget import Widget


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

        self._set_up_layout(block)
        self._initialize_internal_observers()

        self.index = block.index  # Update the spinners

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.parent}, {self.spinners})"

    @property
    def index(self) -> int:
        """The index the block is in for the tsa"""
        return self.block.index

    @index.setter
    def index(self, index: int) -> None:
        self.block.index = index

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
    def pattern_table(self) -> PatternTableHandler:
        """The pattern table for the tiles"""
        return self.block.pattern_table

    @pattern_table.setter
    def pattern_table(self, pattern_table: PatternTableHandler) -> None:
        self.block.pattern_table = pattern_table

    @property
    def palette_set(self) -> PaletteSet:
        """The palette currently used by the tsa"""
        return self.block.palette_set

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

    def _set_up_layout(self, block: AbstractBlock) -> None:
        """Returns the widgets layout"""
        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)

        self.block = BlockTileTrackableObject(self, "Block", block)

        self.spinners = []
        for idx in range(4):
            spinner = HexSpinner(self, maximum=0xFF)
            x, y = idx & 1, idx // 2 * 2
            grid.addWidget(spinner, x, y)
            self.spinners.append(spinner)
        grid.addWidget(self.block, 0, 1, 0, 1, Qt.AlignCenter)

        self.setLayout(grid)

    def _initialize_internal_observers(self) -> None:
        """Initializes internal observers for special events"""
        name = {self.__class__.__name__}

        def update_block_pattern_closure(index):
            """Updates the block pattern"""
            def update_block_pattern(new_pattern):
                """The inner function"""
                old_pattern = self.tsa_data[self.index + (index * 0x100)]
                if new_pattern != old_pattern:
                    self.tsa_data[self.index + (index * 0x100)] = new_pattern
                    self._push_block_update()
            return update_block_pattern

        for idx, spinner in enumerate(self.spinners):
            spinner.value_changed_action.observer.attach_observer(
                update_block_pattern_closure(idx), name=f"{name} Update Block Pattern"
            )

        def update_spinner_closure(index):
            """Updates the spinner of the new tile"""
            def update_spinner(*_):
                """Updates the spinner"""
                if self.spinners[index].value() != (new_pattern := (self.tsa_data[self.index + (index * 0x100)])):
                    self.spinners[index].setValue(new_pattern)
            return update_spinner

        for idx, spinner in enumerate(self.spinners):
            self.block.tsa_data_update_action.observer.attach_observer(
                update_spinner_closure(idx), name=f"{name} Update Spinner {idx}"
            )
            self.block.index_update_action.observer.attach_observer(
                update_spinner_closure(idx), name=f"{name} Update Spinner {idx}"
            )

    def _push_block_update(self) -> None:
        """Pushes an update to the block"""
        for idx, spinner in enumerate(self.spinners):
            if value := (spinner.value()) != self.tsa_data[(idx * 256) + self.index]:
                self.tsa_data[(idx * 256) + self.index] = value
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


