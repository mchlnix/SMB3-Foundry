from typing import Tuple

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
        source_obj = self.level.objects[self.start.tile_data_index]
        source_obj.change_type(self.tile_after)

        if self.end.tile_data_index < len(self.level.objects):
            target_obj = self.level.objects[self.end.tile_data_index]
            target_obj.change_type(self.tile_before)

    def redo(self):
        source_obj = self.level.objects[self.start.tile_data_index]
        source_obj.change_type(WORLD_MAP_BLANK_TILE_ID)

        if self.end.tile_data_index < len(self.level.objects):
            target_obj = self.level.objects[self.end.tile_data_index]
            target_obj.change_type(self.tile_after)
