from typing import Tuple

from PySide6.QtCore import QPoint, QRect, QSize
from PySide6.QtGui import QColor

from foundry.game.gfx.objects.world_map.map_object import MapObject
from smb3parse.constants import MAPOBJ_NAMES, MAP_OBJ_SPRITES
from smb3parse.data_points import Position, SpriteData
from smb3parse.levels import FIRST_VALID_ROW


class Sprite(MapObject):
    def __init__(self, sprite_data: SpriteData):
        super(Sprite, self).__init__()

        self.data = sprite_data

        if self.data.row < FIRST_VALID_ROW:
            self.data.row = FIRST_VALID_ROW

    @property
    def name(self):
        return f"Sprite '{MAPOBJ_NAMES[self.data.type]}'"

    @name.setter
    def name(self, value):
        pass

    def draw(self, painter, block_length, transparent, selected=False):
        pos = QPoint(*self.data.pos.xy) * block_length

        rect = QRect(pos, QSize(block_length, block_length))

        painter.drawImage(rect.topLeft(), MAP_OBJ_SPRITES[self.data.type].scaled(block_length, block_length))

        if selected:
            painter.fillRect(rect, QColor(0x00, 0xFF, 0x00, 0x80))

    def set_position(self, x, y):
        self.data.pos = Position.from_xy(x, y)

    def get_position(self) -> Tuple[int, int]:
        return self.data.pos.xy

    def change_type(self, new_type):
        self.data.type = new_type
