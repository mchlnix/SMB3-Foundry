from PySide6.QtCore import QPoint, QRect, QSize
from PySide6.QtGui import QColor

from foundry.game.gfx.drawable import load_from_png
from foundry.game.gfx.objects.world_map.map_object import MapObject
from smb3parse.constants import (
    MAPITEM_ANCHOR,
    MAPITEM_FIREFLOWER,
    MAPITEM_FROG,
    MAPITEM_HAMMER,
    MAPITEM_HAMMERSUIT,
    MAPITEM_JUDGEMS,
    MAPITEM_LEAF,
    MAPITEM_MUSHROOM,
    MAPITEM_MUSICBOX,
    MAPITEM_NOITEM,
    MAPITEM_PWING,
    MAPITEM_STAR,
    MAPITEM_TANOOKI,
    MAPITEM_UNKNOWN1,
    MAPITEM_UNKNOWN2,
    MAPITEM_WHISTLE,
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
    MAPOBJ_NAMES,
    MAPOBJ_NSPADE,
    MAPOBJ_TANK,
    MAPOBJ_UNK08,
    MAPOBJ_UNK0C,
    MAPOBJ_W7PLANT,
    MAPOBJ_W8AIRSHIP,
    MAPOBJ_WHITETOADHOUSE,
)
from smb3parse.data_points import Position, SpriteData
from smb3parse.levels import FIRST_VALID_ROW


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


EMPTY_IMAGE = load_from_png(0, 53)

MAP_ITEM_SPRITES = {
    MAPITEM_NOITEM: EMPTY_IMAGE,
    MAPITEM_MUSHROOM: load_from_png(6, 48),
    MAPITEM_FIREFLOWER: load_from_png(16, 53),
    MAPITEM_LEAF: load_from_png(57, 53),
    MAPITEM_FROG: load_from_png(56, 53),
    MAPITEM_TANOOKI: load_from_png(54, 53),
    MAPITEM_HAMMERSUIT: load_from_png(58, 53),
    MAPITEM_JUDGEMS: load_from_png(19, 51),
    MAPITEM_PWING: load_from_png(55, 53),
    MAPITEM_STAR: load_from_png(5, 48),
    MAPITEM_ANCHOR: load_from_png(61, 53),
    MAPITEM_HAMMER: load_from_png(63, 53),
    MAPITEM_WHISTLE: load_from_png(60, 53),
    MAPITEM_MUSICBOX: load_from_png(62, 53),
    MAPITEM_UNKNOWN1: EMPTY_IMAGE,
    MAPITEM_UNKNOWN2: EMPTY_IMAGE,
}


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

    @property
    def type(self):
        return self.data.type

    @type.setter
    def type(self, value):
        self.change_type(value)

    def draw(self, painter, block_length, transparent, selected=False):
        pos = QPoint(*self.data.pos.xy) * block_length

        rect = QRect(pos, QSize(block_length, block_length))

        painter.drawImage(rect.topLeft(), MAP_OBJ_SPRITES[self.data.type].scaled(block_length, block_length))

        if selected:
            painter.fillRect(rect, QColor(0x00, 0xFF, 0x00, 0x80))

    def set_position(self, x, y):
        self.data.pos = Position.from_xy(x, y)

    def get_position(self) -> tuple[int, int]:
        return self.data.pos.xy

    def change_type(self, new_type):
        self.data.type = new_type
