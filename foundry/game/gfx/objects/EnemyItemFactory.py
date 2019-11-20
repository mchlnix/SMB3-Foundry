from PySide2.QtCore import QRect
from PySide2.QtGui import QImage

from foundry.game.gfx.Palette import load_palette
from foundry.game.gfx.drawable.Block import Block
from foundry.game.gfx.objects.EnemyItem import EnemyObject


class EnemyItemFactory:
    object_set: int
    graphic_set: int

    definitions: list = []

    def __init__(self, object_set, palette_index):
        png = QImage("data/gfx.png")

        png.convertTo(QImage.Format_RGB888)

        rows_per_object_set = 256 // 64

        y_offset = 12 * rows_per_object_set * Block.HEIGHT

        self.png_data = png.copy(QRect(0, y_offset, png.width(), png.height() - y_offset))

        self.palette_group = load_palette(object_set, palette_index)

    def make_object(self, data, _):
        return EnemyObject(data, self.png_data, self.palette_group)
