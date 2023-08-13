from PySide6.QtCore import QRect
from PySide6.QtGui import QImage

from foundry import data_dir
from foundry.game.gfx.drawable.Block import Block
from foundry.game.gfx.objects import EnemyItem
from foundry.game.gfx.Palette import load_palette_group

ENEMY_ITEM_SPRITE_SHEET = QImage(str(data_dir.joinpath("gfx.png")))

ENEMY_ITEM_SPRITE_SHEET.convertTo(QImage.Format_RGB888)


class EnemyItemFactory:
    object_set: int
    graphic_set: int

    definitions: list = []

    def __init__(self, object_set: int, palette_index=0):
        rows_per_object_set = 256 // 64

        y_offset = 12 * rows_per_object_set * Block.HEIGHT

        self.png_data = ENEMY_ITEM_SPRITE_SHEET.copy(
            QRect(
                0,
                y_offset,
                ENEMY_ITEM_SPRITE_SHEET.width(),
                ENEMY_ITEM_SPRITE_SHEET.height() - y_offset,
            )
        )

        self.palette_group = load_palette_group(object_set, palette_index)

    def from_data(self, data, _):
        return EnemyItem(data, self.png_data, self.palette_group)

    def from_properties(self, enemy_item_id: int, x=0, y=0):
        data = bytearray(3)

        data[0] = enemy_item_id
        data[1] = x
        data[2] = y

        obj = self.from_data(data, 0)

        return obj
