from typing import List

from PySide2.QtCore import QPoint
from PySide2.QtGui import QImage, QPainter, Qt, QColor

from foundry.game.gfx.Palette import NESPalette
from foundry.game.gfx.PatternTable import PatternTable
from foundry.game.gfx.drawable import MASK_COLOR
from foundry.game.gfx.drawable.Tile import Tile

TSA_BANK_0 = 0 * 256
TSA_BANK_1 = 1 * 256
TSA_BANK_2 = 2 * 256
TSA_BANK_3 = 3 * 256


class Block:
    SIDE_LENGTH = 2 * Tile.SIDE_LENGTH
    WIDTH = SIDE_LENGTH
    HEIGHT = SIDE_LENGTH

    PIXEL_COUNT = WIDTH * HEIGHT

    tsa_data = bytes()

    def __init__(
        self,
        block_index: int,
        palette_group: List[List[int]],
        pattern_table: PatternTable,
        tsa_data: bytes,
        mirrored=False,
    ):
        self.index = block_index

        palette_index = (block_index & 0b1100_0000) >> 6

        self.bg_color = NESPalette[palette_group[palette_index][0]]

        lu = tsa_data[TSA_BANK_0 + block_index]
        ld = tsa_data[TSA_BANK_1 + block_index]
        ru = tsa_data[TSA_BANK_2 + block_index]
        rd = tsa_data[TSA_BANK_3 + block_index]

        self.lu_tile = Tile(lu, palette_group, palette_index, pattern_table)
        self.ld_tile = Tile(ld, palette_group, palette_index, pattern_table)

        if mirrored:
            self.ru_tile = Tile(lu, palette_group, palette_index, pattern_table, mirrored=True)
            self.rd_tile = Tile(ld, palette_group, palette_index, pattern_table, mirrored=True)
        else:
            self.ru_tile = Tile(ru, palette_group, palette_index, pattern_table)
            self.rd_tile = Tile(rd, palette_group, palette_index, pattern_table)

        self.image = QImage(Block.WIDTH, Block.HEIGHT, QImage.Format_RGB888)
        painter = QPainter(self.image)

        painter.drawImage(QPoint(0, 0), self.lu_tile.as_image())
        painter.drawImage(QPoint(Tile.WIDTH, 0), self.ru_tile.as_image())
        painter.drawImage(QPoint(0, Tile.HEIGHT), self.ld_tile.as_image())
        painter.drawImage(QPoint(Tile.WIDTH, Tile.HEIGHT), self.rd_tile.as_image())

        painter.end()

        if self.image.colorCount() == 1 and self.image.pixelColor(0, 0) == QColor(*MASK_COLOR):
            self._whole_block_is_transparent = True
        else:
            self._whole_block_is_transparent = False

    def draw(self, painter: QPainter, x, y, block_length, selected=False, transparent=False):
        image = self.image.copy()

        if block_length != Block.WIDTH:
            image = image.scaled(block_length, block_length)

        # todo better effect
        if False and selected:
            image.convertTo(QImage.Format_Mono)

        if not transparent or self._whole_block_is_transparent:
            mask = image.createMaskFromColor(QColor(*MASK_COLOR).rgb(), Qt.MaskMode.MaskOutColor)
            image.setAlphaChannel(mask)

        painter.drawImage(x, y, image)
