from typing import Tuple

from PySide6.QtGui import QUndoCommand

from foundry.game.ObjectSet import OBJECT_SET_NAMES
from foundry.game.gfx.drawable.Block import get_worldmap_tile
from foundry.game.gfx.objects import LevelPointer, Lock
from foundry.game.gfx.objects.world_map.map_object import MapObject
from foundry.game.level.WorldMap import WorldMap
from smb3parse.constants import MAPITEM_NAMES, MAPOBJ_NAMES, TILE_NAMES
from smb3parse.data_points import LevelPointerData, Position, SpriteData
from smb3parse.levels import FIRST_VALID_ROW, WORLD_MAP_BLANK_TILE_ID


class MoveTile(QUndoCommand):
    def __init__(self, world: WorldMap, start: Position, tile_after: int, end: Position, parent=None):
        super(MoveTile, self).__init__(parent)

        self.world = world

        self.start = start
        self.tile_after = tile_after

        self.end = end

        if self.world.point_in(*end.xy):
            self.tile_before = self.world.objects[self.end.tile_data_index].type
        else:
            self.tile_before = WORLD_MAP_BLANK_TILE_ID

        self.setText(f"Move Tile '{TILE_NAMES[tile_after]}'")

    def undo(self):
        if 0 <= self.start.tile_data_index < len(self.world.objects):
            source_obj = self.world.objects[self.start.tile_data_index]
            source_obj.change_type(self.tile_after)
            source_obj.selected = True

        if 0 <= self.end.tile_data_index < len(self.world.objects):
            target_obj = self.world.objects[self.end.tile_data_index]
            target_obj.change_type(self.tile_before)
            target_obj.selected = False

    def redo(self):
        if 0 <= self.start.tile_data_index < len(self.world.objects):
            source_obj = self.world.objects[self.start.tile_data_index]
            source_obj.change_type(WORLD_MAP_BLANK_TILE_ID)
            source_obj.selected = False

        if self.end.tile_data_index < len(self.world.objects):
            target_obj = self.world.objects[self.end.tile_data_index]
            target_obj.change_type(self.tile_after)
            target_obj.selected = True


class MoveMapObject(QUndoCommand):
    def __init__(self, world: WorldMap, map_object: MapObject, end: Position, start: Position = None, parent=None):
        super(MoveMapObject, self).__init__(parent)

        self.world = world

        self.map_object = map_object

        if start is None:
            self.start = map_object.get_position()
        else:
            self.start = start.xy

        self.end = end.xy

        self.setText(f"Move {self.map_object.name}")

    def undo(self):
        self._move_map_object(self.start)

    def redo(self):
        self._move_map_object(self.end)

    def _move_map_object(self, new_pos: Tuple[int, int]):
        self.map_object.set_position(*new_pos)

        if isinstance(self.map_object, Lock):
            for lock in self.world.locks_and_bridges:
                if lock.data.index == self.map_object.data.index:
                    lock.set_position(*new_pos)

        self.world.data_changed.emit()


class PutTile(MoveTile):
    """Implemented by doing an illegal move from outside the Map. Should probably be the other way around."""

    def __init__(self, world: WorldMap, pos: Position, tile_index: int, parent=None):
        super(PutTile, self).__init__(
            world, start=Position.from_xy(-1, -1), tile_after=tile_index, end=pos, parent=parent
        )

    def redo(self):
        super(PutTile, self).redo()

        for obj in self.world.objects:
            obj.selected = False


class WorldPaletteIndex(QUndoCommand):
    def __init__(self, world: WorldMap, new_index: int):
        super(WorldPaletteIndex, self).__init__()

        self.world = world
        self.old_index = world.data.palette_index
        self.new_index = new_index

    def undo(self):
        self.world.data.palette_index = self.old_index

        self.world.palette_changed.emit()

    def redo(self):
        self.world.data.palette_index = self.new_index

        self.world.palette_changed.emit()


class SetLevelAddress(QUndoCommand):
    def __init__(self, data: LevelPointerData, new_address: int, parent=None):
        super(SetLevelAddress, self).__init__(parent)

        self.data = data

        self.old_address = data.level_address
        self.new_address = new_address

        self.setText(f"Set LP #{self.data.index + 1} Level Address to {hex(new_address)}")

    def undo(self):
        self.data.level_address = self.old_address

    def redo(self):
        self.data.level_address = self.new_address


class SetEnemyAddress(QUndoCommand):
    def __init__(self, data: LevelPointerData, new_address: int, parent=None):
        super(SetEnemyAddress, self).__init__(parent)

        self.data = data

        self.old_address = data.enemy_address
        self.new_address = new_address

        self.setText(f"Set LP #{self.data.index + 1} Enemy Address to {hex(new_address)}")

    def undo(self):
        self.data.enemy_address = self.old_address

    def redo(self):
        self.data.enemy_address = self.new_address


class SetObjectSet(QUndoCommand):
    def __init__(self, data: LevelPointerData, object_set_number: int, parent=None):
        super(SetObjectSet, self).__init__(parent)

        self.data = data

        self.old_object_set = data.object_set
        self.new_object_set = object_set_number

        self.setText(f"Set LP #{self.data.index + 1} Object Set to {OBJECT_SET_NAMES[object_set_number]}")

    def undo(self):
        self.data.object_set = self.old_object_set

    def redo(self):
        self.data.object_set = self.new_object_set


class SetSpriteType(QUndoCommand):
    def __init__(self, data: SpriteData, new_type: int, parent=None):
        super(SetSpriteType, self).__init__(parent)

        self.data = data

        self.old_type = self.data.type
        self.new_type = new_type

        self.setText(f"Set Sprite #{self.data.index  +1} Type to {MAPOBJ_NAMES[new_type]}")

    def undo(self):
        self.data.type = self.old_type

    def redo(self):
        self.data.type = self.new_type


class SetSpriteItem(QUndoCommand):
    def __init__(self, data: SpriteData, new_item: int, parent=None):
        super(SetSpriteItem, self).__init__(parent)

        self.data = data

        self.old_item = self.data.item
        self.new_item = new_item

        self.setText(f"Set Sprite #{self.data.index + 1} Item to {MAPITEM_NAMES[new_item]}")

    def undo(self):
        self.data.item = self.old_item

    def redo(self):
        self.data.item = self.new_item


class SetScreenCount(QUndoCommand):
    def __init__(self, world: WorldMap, screen_count: int, parent=None):
        super(SetScreenCount, self).__init__(parent)

        self.world = world

        self.old_screen_count = self.world.data.screen_count
        # FIXME: only works, because self.world.objects is in the same order as tile_data
        self.old_world_data = [map_tile.type for map_tile in self.world.objects]
        self.new_screen_count = screen_count

        self.setText(f"Set World {self.world.internal_world_map.world_index + 1}'s screen count to {screen_count}")

    def undo(self):
        self.world.data.screen_count = self.old_screen_count
        self.world.data.tile_data = self.old_world_data
        self.world.reread_tiles()

    def redo(self):
        self.world.data.screen_count = self.new_screen_count
        self.world.reread_tiles()


class ChangeReplacementTile(QUndoCommand):
    def __init__(self, world: WorldMap, fortress_fx_index: int, replacement_tile_index: int, parent=None):
        super(ChangeReplacementTile, self).__init__(parent)

        self.world = world
        self.fx_index = fortress_fx_index
        self.replacement_tile_index = replacement_tile_index

        self.old_replacement_tile_index = -1
        self.old_tile_indexes = []

    def undo(self):
        for lock in self.world.locks_and_bridges:
            if lock.data.index == self.fx_index:
                lock.data.tile_indexes = self.old_tile_indexes
                lock.data.replacement_block_index = self.old_replacement_tile_index

    def redo(self):
        block = get_worldmap_tile(self.replacement_tile_index)

        for lock in self.world.locks_and_bridges:
            if lock.data.index == self.fx_index:
                self.old_tile_indexes = lock.data.tile_indexes
                self.old_replacement_tile_index = lock.data.replacement_block_index

                lock.data.tile_indexes = [
                    block.lu_tile.tile_index,
                    block.ru_tile.tile_index,
                    block.ld_tile.tile_index,
                    block.rd_tile.tile_index,
                ]
                lock.data.replacement_block_index = self.replacement_tile_index


class ChangeLockIndex(QUndoCommand):
    def __init__(self, world: WorldMap, lock: Lock, new_index: int, parent=None):
        super(ChangeLockIndex, self).__init__(parent)

        self.world = world
        self.lock = lock

        self.old_index = lock.data.index
        self.old_replacement_tile = lock.data.replacement_block_index
        self.new_index = new_index

    def undo(self):
        self._change_lock_index(self.old_index)

    def redo(self):
        self._change_lock_index(self.new_index)

    def _change_lock_index(self, new_index: int):
        if self.old_index == self.new_index:
            return

        for lock in self.world.locks_and_bridges:
            if lock is self.lock:
                continue

            if lock.data.index == new_index:
                self.lock.data.change_index(new_index)
                self.lock.data.replacement_block_index = lock.data.replacement_block_index
                self.lock.data.set_pos(lock.data.pos)

                break

        else:
            self.lock.data.change_index(new_index)
            self.lock.data.read_values()


class SetWorldIndex(QUndoCommand):
    def __init__(self, world: WorldMap, new_index: int, parent=None):
        super(SetWorldIndex, self).__init__(parent)

        self.world = world

        self.old_index = world.data.index
        self.new_index = new_index

        self.setText(f"Set World {self.world.internal_world_map.world_index + 1}'s index to {new_index + 1}")

    def undo(self):
        self.world.data.change_index(self.old_index)
        self.world.reread_tiles()

    def redo(self):
        self.world.data.change_index(self.new_index)
        self.world.reread_tiles()


class ChangeSpriteIndex(QUndoCommand):
    def __init__(self, world: WorldMap, old_index: int, new_index: int, parent=None):
        super(ChangeSpriteIndex, self).__init__(parent)
        self.world = world

        self.old_index = old_index
        self.new_index = new_index

        self.setText(f"Change Sprite Index {self.old_index} -> {self.new_index}")

    def undo(self):
        self.world.move_sprites(self.new_index, self.old_index)

    def redo(self):
        self.world.move_sprites(self.old_index, self.new_index)


class ChangeLevelPointerIndex(QUndoCommand):
    def __init__(self, world: WorldMap, old_index: int, new_index: int, parent=None):
        super(ChangeLevelPointerIndex, self).__init__(parent)
        self.world = world

        self.old_index = old_index
        self.new_index = new_index

        self.setText(f"Change Level Pointer Index {self.old_index} -> {self.new_index}")

    def undo(self):
        self.world.move_level_pointers(self.new_index, self.old_index)

    def redo(self):
        self.world.move_level_pointers(self.old_index, self.new_index)


class AddLevelPointer(QUndoCommand):
    def __init__(self, world: WorldMap, parent=None):
        super(AddLevelPointer, self).__init__(parent)

        self.world = world

        self.setText("Add Level Pointer")

    def undo(self):
        self.world.data.level_count_screen_1 -= 1
        self.world.data.level_pointers.pop(0)
        self.world.level_pointers.pop(0)

    def redo(self):
        self.world.data.level_count_screen_1 += 1

        new_level_pointer = LevelPointerData(self.world.data, self.world.data.level_count)
        new_level_pointer.pos = Position(FIRST_VALID_ROW, 0, 0)
        new_level_pointer.object_set = 1
        new_level_pointer.level_address = 0x0
        new_level_pointer.enemy_address = 0x0

        self.world.data.level_pointers.insert(0, new_level_pointer)

        self.world.level_pointers.insert(0, LevelPointer(new_level_pointer))


class RemoveLevelPointer(QUndoCommand):
    def __init__(self, world: WorldMap, index=-1, parent=None):
        super(RemoveLevelPointer, self).__init__(parent)

        self.world = world

        if index == -1:
            index = self.world.data.level_count - 1

        self.index = index

        self.removed_level_pointer = self.world.data.level_pointers[index]

        self.setText(f"Remove Level Pointer #{index}")

    def undo(self):
        # TODO not nice
        attr_name = f"level_count_screen_{self.removed_level_pointer.screen + 1}"

        lvls_on_screen = getattr(self.world.data, f"level_count_screen_{self.removed_level_pointer.screen + 1}")

        setattr(self.world.data, attr_name, lvls_on_screen + 1)

        self.world.data.level_pointers.insert(self.index, self.removed_level_pointer)
        self.world.level_pointers.insert(self.index, LevelPointer(self.removed_level_pointer))

    def redo(self):
        # TODO not nice
        attr_name = f"level_count_screen_{self.removed_level_pointer.screen + 1}"

        lvls_on_screen = getattr(self.world.data, f"level_count_screen_{self.removed_level_pointer.screen + 1}")

        assert lvls_on_screen > 0

        setattr(self.world.data, attr_name, lvls_on_screen - 1)

        self.world.data.level_pointers.pop(self.index)
        self.world.level_pointers.pop(self.index)
