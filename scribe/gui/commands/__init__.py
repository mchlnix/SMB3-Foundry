from PySide6.QtGui import QUndoCommand

from foundry.game.ObjectSet import OBJECT_SET_NAMES
from foundry.game.gfx.objects.world_map.map_object import MapObject
from foundry.game.level.WorldMap import WorldMap
from smb3parse.constants import MAPITEM_NAMES, MAPOBJ_NAMES, TILE_NAMES
from smb3parse.data_points import LevelPointerData, Position, SpriteData
from smb3parse.levels import WORLD_MAP_BLANK_TILE_ID


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
        self.map_object.set_position(*self.start)

    def redo(self):
        self.map_object.set_position(*self.end)


class PutTile(MoveTile):
    """Implemented by doing an illegal move from outside the Map. Should probably be the other way around."""

    def __init__(self, world: WorldMap, pos: Position, tile_index: int, parent=None):
        super(PutTile, self).__init__(
            world, start=Position.from_xy(-1, -1), tile_after=tile_index, end=pos, parent=parent
        )


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
