from typing import Tuple

from PySide6.QtCore import QPoint, QRect, QSize
from PySide6.QtGui import QColor

from foundry.game.gfx.drawable import load_from_png
from foundry.game.gfx.objects.world_map.map_object import MapObject
from smb3parse.constants import (
    MAPOBJ_AIRSHIP,
    MAPOBJ_BATTLESHIP,
    MAPOBJ_BOOMERANGBRO,
    MAPOBJ_CANOE,
    MAPOBJ_COINSHIP,
    MAPOBJ_EMPTY,
    MAPOBJ_FIREBRO,
    MAPOBJ_HAMMERBRO,
    MAPOBJ_HEAVYBRO,
    MAPOBJ_HELP,
    MAPOBJ_NSPADE,
    MAPOBJ_TANK,
    MAPOBJ_UNK08,
    MAPOBJ_UNK0C,
    MAPOBJ_W7PLANT,
    MAPOBJ_W8AIRSHIP,
    MAPOBJ_WHITETOADHOUSE,
)
from smb3parse.data_points import Position, SpriteData

EMPTY_IMAGE = load_from_png(0, 53)

MAP_OBJ_SPRITES = {
    MAPOBJ_EMPTY: EMPTY_IMAGE,
    MAPOBJ_HELP: load_from_png(43, 2),
    MAPOBJ_AIRSHIP: load_from_png(44, 2),
    MAPOBJ_HAMMERBRO: load_from_png(45, 2),
    MAPOBJ_BOOMERANGBRO: load_from_png(46, 2),
    MAPOBJ_HEAVYBRO: load_from_png(47, 2),
    MAPOBJ_FIREBRO: load_from_png(48, 2),
    MAPOBJ_W7PLANT: load_from_png(49, 2),
    MAPOBJ_UNK08: load_from_png(50, 2),
    MAPOBJ_NSPADE: load_from_png(51, 2),
    MAPOBJ_WHITETOADHOUSE: load_from_png(52, 2),
    MAPOBJ_COINSHIP: load_from_png(53, 2),
    MAPOBJ_UNK0C: load_from_png(54, 2),
    MAPOBJ_BATTLESHIP: load_from_png(55, 2),
    MAPOBJ_TANK: load_from_png(56, 2),
    MAPOBJ_W8AIRSHIP: load_from_png(57, 2),
    MAPOBJ_CANOE: load_from_png(58, 2),
}


class Sprite(MapObject):
    def __init__(self, sprite_data: SpriteData):
        super(Sprite, self).__init__(sprite_data.pos)

        self.data = sprite_data

    def draw(self, painter, block_length, transparent, selected=False):
        pos = QPoint(*self.data.pos.xy) * block_length

        rect = QRect(pos, QSize(block_length, block_length))

        painter.drawImage(rect.topLeft(), MAP_OBJ_SPRITES[self.data.type].scaled(block_length, block_length))

        if selected:
            painter.fillRect(rect, QColor(0x00, 0xFF, 0x00, 0x80))

    def set_position(self, x, y):
        self.data.pos = Position.from_xy(x, y)

    def move_by(self, dx, dy):
        x, y = self.get_position()
        new_x = x + dx
        new_y = y + dy

        self.set_position(new_x, new_y)

    def get_position(self) -> Tuple[int, int]:
        return self.data.pos.xy

    def point_in(self, x, y):
        return x, y == self.get_position()

    def change_type(self, new_type):
        self.data.type = new_type
