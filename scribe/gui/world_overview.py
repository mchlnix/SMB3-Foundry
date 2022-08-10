import typing
from typing import Dict, List

from PySide6.QtCore import Signal, SignalInstance
from PySide6.QtGui import QDropEvent, QUndoStack
from PySide6.QtWidgets import QTableWidgetItem

from foundry.game.File import ROM
from foundry.game.level.LevelRef import LevelRef
from foundry.gui.Spinner import Spinner
from scribe.gui.commands import AddLevelPointer, RemoveLevelPointer, SetScreenCount, SetStructureBlockAddress, \
    SetTileDataOffset, \
    SetWorldIndex
from scribe.gui.tool_window.locks_list import NoneDelegate
from scribe.gui.tool_window.table_widget import SpinBoxDelegate, TableWidget
from smb3parse.constants import GAME_LEVEL_POINTER_COUNT, GAME_SCREEN_COUNT, SPRITE_COUNT
from smb3parse.data_points import SpriteData, WorldMapData
from smb3parse.levels import WORLD_COUNT
from smb3parse.util.rom import Rom


class _WorldDataStandIn:
    def __init__(self, world_data: WorldMapData):
        self.level_count = world_data.level_count
        self.screen_count = world_data.screen_count
        self.index = world_data.index

        self.sprites = [SpriteData(world_data, index) for index in range(SPRITE_COUNT)]

        self.data = world_data


class WorldOverview(TableWidget):
    data_changed: SignalInstance = Signal()

    def __init__(self, parent, level_ref: LevelRef, rom: Rom):
        super(WorldOverview, self).__init__(parent, level_ref)

        self.rom = rom
        self.world_data_points: List[_WorldDataStandIn] = []

        self.cellChanged.connect(self._change_data)

        first_world = WorldMapData(rom, 0)

        for world_index in range(WORLD_COUNT - 1):
            if world_index == self.world.data.index:
                self.world_data_points.append(_WorldDataStandIn(self.world.data))
                print(self.world.data.tile_data_offset - first_world.tile_data_offset, len(self.world.data.tile_data) + 1)
                continue

            world_data_point = WorldMapData(rom, world_index)
            print(world_data_point.tile_data_offset - first_world.tile_data_offset, len(world_data_point.tile_data) + 1)
            self.world_data_points.append(_WorldDataStandIn(world_data_point))

        self.set_headers(["World Name", "Screen Count", "Level Count"])

        self.setItemDelegateForColumn(0, NoneDelegate(self))
        self.setItemDelegateForColumn(1, SpinBoxDelegate(self, minimum=1, maximum=4, base=10))
        self.setItemDelegateForColumn(2, SpinBoxDelegate(self, base=10))

        self.update_content()

    def dropEvent(self, event: QDropEvent) -> None:
        source_index = self.selectedIndexes()[0].row()
        target_index = self.indexAt(event.pos()).row()

        source_world = self.world_data_for(source_index)
        target_world = self.world_data_for(target_index)

        print(source_world.index, target_index)
        print(target_world.index, source_index)

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
            screen_count_item = QTableWidgetItem(f"{world_data.screen_count}")
            level_count_item = QTableWidgetItem(f"{world_data.level_count}")

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
        # write tiles back into world map data object, so we can properly undo the screen count change
        self.world.write_tiles()
        undo_stack.beginMacro("Reorganize World Maps")

        world_dict: Dict[int, _WorldDataStandIn] = {world.index : world for world in self.world_data_points}

        first_world = WorldMapData(ROM(), 0)

        structure_block_address = first_world.structure_block_address
        tile_data_offset_running_total = first_world.tile_data_offset

        for index in range(WORLD_COUNT - 1):
            world = world_dict[index]

            undo_stack.push(SetWorldIndex(world.data, world.sprites, index))

            print(index, world.data.screen_count, world.screen_count)

            if index == self.world.data.index:
                world_map = self.world
            else:
                world_map = None

            undo_stack.push(SetScreenCount(world.data, world.screen_count, world_map))

            if (diff := world.data.level_count - world.level_count) == 0:
                pass

            elif diff > 0:
                print(diff)
                for _ in range(diff):
                    undo_stack.push(RemoveLevelPointer(world.data, world=world_map))
            else:
                print(diff)
                for _ in range(abs(diff)):
                    undo_stack.push(AddLevelPointer(world.data, world_map))

            undo_stack.push(SetStructureBlockAddress(world.data, structure_block_address))
            structure_block_address += world.data.structure_block_size

            undo_stack.push(SetTileDataOffset(world.data, tile_data_offset_running_total))
            tile_data_offset_running_total += world.data.tile_data_size

        for index in range(WORLD_COUNT - 1):
            world = world_dict[index]

            world.data.write_back()

            for sprite_data in world.sprites:
                sprite_data.write_back()

        undo_stack.endMacro()

        self.world.reread_tiles()

        self.world.data_changed.emit()

