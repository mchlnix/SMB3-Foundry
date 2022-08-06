from functools import lru_cache
from typing import Dict, Tuple

from PySide6.QtCore import QPoint
from PySide6.QtGui import QColor, QImage, QPainter, Qt

from foundry.game.File import ROM
from foundry.game.gfx.GraphicsSet import GraphicsSet
from foundry.game.gfx.Palette import NESPalette, PaletteGroup, load_palette_group
from foundry.game.gfx.drawable import MASK_COLOR, apply_selection_overlay
from foundry.game.gfx.drawable.Tile import Tile
from smb3parse.objects.object_set import CLOUDY_GRAPHICS_SET, WORLD_MAP_OBJECT_SET

TSA_BANK_0 = 0 * 256
TSA_BANK_1 = 1 * 256
TSA_BANK_2 = 2 * 256
TSA_BANK_3 = 3 * 256


@lru_cache(2**10)
def get_block(block_index: int, palette_group: PaletteGroup, graphics_set: GraphicsSet, tsa_data: bytes):
    if block_index > 0xFF:
        rom_block_index = ROM().get_byte(block_index)  # block_index is an offset into the graphic memory
        block = Block(rom_block_index, palette_group, graphics_set, tsa_data)
    else:
        block = Block(block_index, palette_group, graphics_set, tsa_data)

    return block


def get_tile(index, palette_group, palette_index, graphics_set, mirrored=False):
    return Tile(index, palette_group, palette_index, graphics_set, mirrored)


def get_worldmap_tile(block_index: int, palette_index=0):
    return get_block(
        block_index,
        load_palette_group(WORLD_MAP_OBJECT_SET, palette_index),
        GraphicsSet(0),
        ROM.get_tsa_data(WORLD_MAP_OBJECT_SET),
    )


BlockId = Tuple[int, str, int]


class Block:
    SIDE_LENGTH = 2 * Tile.SIDE_LENGTH
    WIDTH = SIDE_LENGTH
    HEIGHT = SIDE_LENGTH

    PIXEL_COUNT = WIDTH * HEIGHT

    tsa_data = bytes()

    _block_cache: Dict[Tuple[BlockId, int, bool, bool], QImage] = {}

    def __init__(
        self,
        block_index: int,
        palette_group: PaletteGroup,
        graphics_set: GraphicsSet,
        tsa_data: bytes,
        mirrored: bool = False,
    ):
        self.index = block_index

        self.palette_index = (block_index & 0b1100_0000) >> 6
        self.graphics_set = graphics_set
        self.palette_group = palette_group

        self.tsa_data = tsa_data

        self.mirrored = mirrored

        if graphics_set.number == CLOUDY_GRAPHICS_SET:
            self.bg_color = NESPalette[palette_group[self.palette_index][2]]
        else:
            self.bg_color = NESPalette[palette_group[self.palette_index][0]]

        self._render()

    def _render(self):
        # can't hash list, so turn it into a string instead
        self._block_id: BlockId = (self.index, str(self.palette_group), self.graphics_set.number)

        lu = self.tsa_data[TSA_BANK_0 + self.index]
        ld = self.tsa_data[TSA_BANK_1 + self.index]
        ru = self.tsa_data[TSA_BANK_2 + self.index]
        rd = self.tsa_data[TSA_BANK_3 + self.index]

        self.lu_tile = get_tile(lu, self.palette_group, self.palette_index, self.graphics_set)
        self.ld_tile = get_tile(ld, self.palette_group, self.palette_index, self.graphics_set)

        if self.mirrored:
            self.ru_tile = get_tile(lu, self.palette_group, self.palette_index, self.graphics_set, mirrored=True)
            self.rd_tile = get_tile(ld, self.palette_group, self.palette_index, self.graphics_set, mirrored=True)
        else:
            self.ru_tile = get_tile(ru, self.palette_group, self.palette_index, self.graphics_set)
            self.rd_tile = get_tile(rd, self.palette_group, self.palette_index, self.graphics_set)

        self.image = QImage(Block.WIDTH, Block.HEIGHT, QImage.Format_RGB888)
        painter = QPainter(self.image)

        painter.drawImage(QPoint(0, 0), self.lu_tile.as_image())
        painter.drawImage(QPoint(Tile.WIDTH, 0), self.ru_tile.as_image())
        painter.drawImage(QPoint(0, Tile.HEIGHT), self.ld_tile.as_image())
        painter.drawImage(QPoint(Tile.WIDTH, Tile.HEIGHT), self.rd_tile.as_image())

        painter.end()

        if _image_only_one_color(self.image) and self.image.pixelColor(0, 0) == QColor(*MASK_COLOR):
            self._whole_block_is_transparent = True
        else:
            self._whole_block_is_transparent = False

    def rerender(self):
        self._render()

    def draw(self, painter: QPainter, x, y, block_length, selected=False, transparent=False):
        block_attributes = (self._block_id, block_length, selected, transparent, self.graphics_set.anim_frame)

        if True or block_attributes not in Block._block_cache:
            image = self.image.copy()

            if block_length != Block.WIDTH:
                image = image.scaled(block_length, block_length)

            # mask out the transparent pixels first
            mask = image.createMaskFromColor(QColor(*MASK_COLOR).rgb(), Qt.MaskOutColor)
            image.setAlphaChannel(mask)

            if not transparent:  # or self._whole_block_is_transparent:
                image = self._replace_transparent_with_background(image)

            if selected:
                apply_selection_overlay(image, mask)

            Block._block_cache[block_attributes] = image

        painter.drawImage(x, y, Block._block_cache[block_attributes])

    def _replace_transparent_with_background(self, image):
        # draw image on background layer, to fill transparent pixels
        background = image.copy()
        background.fill(self.bg_color)

        _painter = QPainter(background)
        _painter.drawImage(QPoint(), image)
        _painter.end()

        return background


def _image_only_one_color(image):
    copy = image.copy()

    copy.convertTo(QImage.Format_Indexed8)

    return copy.colorCount() == 1
