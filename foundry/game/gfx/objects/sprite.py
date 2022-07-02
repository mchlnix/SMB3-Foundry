from PySide6.QtCore import QPoint, QRect
from PySide6.QtGui import QColor, QPen

from foundry.game.gfx.drawable import load_from_png
from foundry.game.gfx.objects.LevelObject import SCREEN_WIDTH
from foundry.game.gfx.objects.ObjectLike import ObjectLike
from smb3parse.levels import FIRST_VALID_ROW
from smb3parse.levels.data_points import SpriteData
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


class Sprite(ObjectLike):
    def __init__(self, sprite_data: SpriteData):
        super(Sprite, self).__init__()

        self.data = sprite_data

    def render(self):
        pass

    def draw(self, painter, block_length, transparent, selected=False):
        painter.save()

        x = (self.data.screen * SCREEN_WIDTH + self.data.x) * block_length
        y = (self.data.y - FIRST_VALID_ROW) * block_length

        painter.setPen(QPen(QColor(0x00, 0x00, 0xFF, 0x80), 4))
        painter.drawImage(QPoint(x, y), MAP_OBJ_SPRITES[self.data.type].scaled(block_length, block_length))

        if selected:
            painter.fillRect(QRect(x, y, block_length, block_length), QColor(0x00, 0xFF, 0x00, 0x80))

        painter.restore()

    def get_status_info(self):
        return ""

    def set_position(self, x, y):
        self.data.x = x
        self.data.y = y

    def move_by(self, dx, dy):
        self.data.x += dx
        self.data.y += dy

    def get_position(self):
        return self.data.x, self.data.y

    def resize_by(self, dx, dy):
        pass

    def point_in(self, x, y):
        return self.data.x == x and self.data.y == y

    def change_type(self, new_type):
        self.data.type = new_type

    def __contains__(self, point):
        pass

    def to_bytes(self):
        raise NotImplementedError
