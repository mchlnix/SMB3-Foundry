import typing

from PySide6.QtCore import Signal, SignalInstance
from PySide6.QtGui import QDropEvent, QUndoStack
from PySide6.QtWidgets import QTableWidgetItem

from foundry.game.File import ROM
from foundry.game.level.LevelRef import LevelRef
from foundry.gui.widgets.Spinner import Spinner
from scribe.gui.commands import (
    AddLevelPointer,
    RemoveLevelPointer,
    SaveWorldsOnRedo,
    SaveWorldsOnUndo,
    SetScreenCount,
    SetStructureBlockAddress,
    SetTileDataOffset,
    SetWorldIndex,
    WorldDataStandIn,
)
from scribe.gui.tool_window.locks_list import NoneDelegate
from scribe.gui.tool_window.table_widget import SpinBoxDelegate, TableWidget
from smb3parse.constants import GAME_LEVEL_POINTER_COUNT, GAME_SCREEN_COUNT
from smb3parse.data_points import WorldMapData
from smb3parse.levels import WORLD_COUNT
from smb3parse.util.rom import Rom


class WorldOverview(TableWidget):
    data_changed: SignalInstance = Signal()

    def __init__(self, parent, level_ref: LevelRef, rom: Rom):
        super(WorldOverview, self).__init__(parent, level_ref)

        self.rom = rom
        self.world_data_points: list[WorldDataStandIn] = []

        self.cellChanged.connect(self._change_data)

        for world_index in range(WORLD_COUNT - 1):
            if world_index == self.world.data.index:
                self.world_data_points.append(WorldDataStandIn(self.world.data))
                continue

            world_data_point = WorldMapData(rom, world_index)
            self.world_data_points.append(WorldDataStandIn(world_data_point))

        self.set_headers(["World Name", "Screen Count", "Level Count"])

        self.setItemDelegateForColumn(0, NoneDelegate(self))
        self.setItemDelegateForColumn(1, SpinBoxDelegate(self, minimum=1, maximum=4, base=10))
        self.setItemDelegateForColumn(2, SpinBoxDelegate(self, base=10))

        self.update_content()

    def dropEvent(self, event: QDropEvent) -> None:
        source_index = self.selectedIndexes()[0].row()
        target_index = self.indexAt(event.position().toPoint()).row()

        source_world = self.world_data_for(source_index)
        target_world = self.world_data_for(target_index)

        source_world.index = target_index
        target_world.index = source_index

        self.update_content()

        self.data_changed.emit()

    def world_data_for(self, world_index: int):
        for world_data in self.world_data_points:
            if world_data.index == world_index:
                return world_data
        else:
            raise LookupError(f"Couldn't find world with index {world_index}")

    def update_content(self):
        self.setRowCount(len(self.world_data_points))

        self.blockSignals(True)

        for world_number, world_data in enumerate(self.world_data_points, 1):
            row = world_data.index

            name_item = QTableWidgetItem(f"World {world_number}")
            screen_count_item = QTableWidgetItem(str(world_data.screen_count))
            level_count_item = QTableWidgetItem(str(world_data.level_count))

            self.setItem(row, 0, name_item)
            self.setItem(row, 1, screen_count_item)
            self.setItem(row, 2, level_count_item)

        self.blockSignals(False)

    def _change_data(self, row, column):
        world_index = row

        for world_data in self.world_data_points:
            if world_data.index == world_index:
                break
        else:
            return

        if column == 0:
            return

        widget = typing.cast(Spinner, self.cellWidget(row, column))
        data = widget.value()

        if column == 1:
            world_data.screen_count = data
        elif column == 2:
            world_data.level_count = data

        self.data_changed.emit()

    @property
    def level_count(self):
        return sum([world_data.level_count for world_data in self.world_data_points])

    @property
    def screen_count(self):
        return sum([world_data.screen_count for world_data in self.world_data_points])

    @property
    def status_msg(self):
        return (
            f"Your worlds have {self.screen_count}/{GAME_SCREEN_COUNT - 1} screens and "
            f"{self.level_count}/{GAME_LEVEL_POINTER_COUNT} level pointers."
        )

    def valid(self):
        return self.screen_count <= GAME_SCREEN_COUNT - 1 and self.level_count <= GAME_LEVEL_POINTER_COUNT

    def finalize(self, undo_stack: QUndoStack):
        if all(not world.changed for world in self.world_data_points):
            return

        # write tiles back into world map data object, so we can properly undo the screen count change
        self.world.write_tiles()
        undo_stack.beginMacro("Reorganize World Maps")

        undo_stack.push(SaveWorldsOnUndo(self.world_data_points))

        world_dict: dict[int, WorldDataStandIn] = {world.index: world for world in self.world_data_points}

        first_world = WorldMapData(ROM(), 0)

        structure_block_address = first_world.structure_block_address
        tile_data_offset_running_total = first_world.tile_data_offset

        for index in range(WORLD_COUNT - 1):
            world = world_dict[index]

            if world.data.index == self.world.data.index:
                world_map = self.world
            else:
                world_map = None

            undo_stack.push(SetWorldIndex(world.data, world.sprites, index))

            undo_stack.push(SetScreenCount(world.data, world.screen_count, world_map))

            if (diff := world.data.level_count - world.level_count) == 0:
                pass

            elif diff > 0:
                for _ in range(diff):
                    undo_stack.push(RemoveLevelPointer(world.data, world=world_map))
            else:
                for _ in range(abs(diff)):
                    undo_stack.push(AddLevelPointer(world.data, world_map))

            undo_stack.push(SetStructureBlockAddress(world.data, structure_block_address))
            structure_block_address += world.data.structure_block_size

            undo_stack.push(SetTileDataOffset(world.data, tile_data_offset_running_total))
            tile_data_offset_running_total += world.data.tile_data_size

        undo_stack.push(SaveWorldsOnRedo(self.world_data_points))

        undo_stack.endMacro()

        self.world.reread_tiles()

        self.world.data_changed.emit()
