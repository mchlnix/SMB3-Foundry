from PySide6.QtGui import QUndoCommand

from foundry.game.gfx.objects.world_map.map_object import MapObject
from foundry.game.level.WorldMap import WorldMap
from smb3parse.data_points import Position
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

        if start == end:
            self.setObsolete(True)

    def undo(self):
        if 0 <= self.start.tile_data_index < len(self.world.objects):
            source_obj = self.world.objects[self.start.tile_data_index]
            source_obj.change_type(self.tile_after)

        if 0 <= self.end.tile_data_index < len(self.world.objects):
            target_obj = self.world.objects[self.end.tile_data_index]
            target_obj.change_type(self.tile_before)

    def redo(self):
        if 0 <= self.start.tile_data_index < len(self.world.objects):
            source_obj = self.world.objects[self.start.tile_data_index]
            source_obj.change_type(WORLD_MAP_BLANK_TILE_ID)

        if self.end.tile_data_index < len(self.world.objects):
            target_obj = self.world.objects[self.end.tile_data_index]
            target_obj.change_type(self.tile_after)


class MoveMapObject(QUndoCommand):
    def __init__(self, world: WorldMap, map_object: MapObject, start: Position, parent=None):
        super(MoveMapObject, self).__init__(parent)

        self.world = world

        self.map_object = map_object

        self.start = start.xy
        self.end = self.map_object.get_position()

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
