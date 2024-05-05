from functools import lru_cache

from PySide6.QtCore import QPoint
from PySide6.QtGui import QColor, QImage, QPainter, Qt

from foundry.game.File import ROM
from foundry.game.gfx.drawable import MASK_COLOR, apply_selection_overlay
from foundry.game.gfx.drawable.Tile import Tile
from foundry.game.gfx.GraphicsSet import GraphicsSet
from foundry.game.gfx.Palette import NESPalette, PaletteGroup, load_palette_group
from smb3parse.objects.object_set import CLOUDY_GRAPHICS_SET, WORLD_MAP_OBJECT_SET

TSA_BANK_0_START = 0 * 256
TSA_BANK_1_START = 1 * 256
TSA_BANK_2_START = 2 * 256
TSA_BANK_3_START = 3 * 256


@lru_cache(2**10)
def get_block(
    block_index: int,
    palette_group: PaletteGroup,
    graphics_set: GraphicsSet,
    tsa_data: bytes,
):
    if block_index > 0xFF:
        rom_block_index = ROM().int(block_index)  # block_index is an offset into the graphic memory
        block = Block(rom_block_index, palette_group, graphics_set, tsa_data)
    else:
        block = Block(block_index, palette_group, graphics_set, tsa_data)

    return block


@lru_cache(2**10)
def get_tile(index, palette_group, palette_index, graphics_set):
    return Tile(index, palette_group, palette_index, graphics_set)


def get_worldmap_tile(block_index: int, palette_index=0):
    return get_block(
        block_index,
        load_palette_group(WORLD_MAP_OBJECT_SET, palette_index),
        GraphicsSet.from_number(0),
        ROM.get_tsa_data(WORLD_MAP_OBJECT_SET),
    )


BlockId = tuple[int, str, int]


class Block:
    """
    A Block is 16 pixels high and wide and is the smallest drawable unit in the game.
    Some objects are only one block (e.g. coin block), others are made up of many different blocks (e.g. bushes).

    A Block consists of four tiles, that are selected by the tsa data, which contain indexes into the graphics set.
    The graphics set has a color index for each pixel in the tile, which corresponds to a color in the block's palette.
    """

    SIDE_LENGTH = 2 * Tile.SIDE_LENGTH
    WIDTH = SIDE_LENGTH
    HEIGHT = SIDE_LENGTH

    PIXEL_COUNT = WIDTH * HEIGHT

    _tsa_data = bytes()

    _block_cache: dict[tuple[BlockId, int, bool, bool, int], QImage] = {}

    def __init__(
        self,
        block_index: int,
        palette_group: PaletteGroup,
        graphics_set: GraphicsSet,
        tsa_data: bytes,
    ):
        self.index = block_index
        self.graphics_set = graphics_set

        self._palette_index = (block_index & 0b1100_0000) >> 6
        self._palette_group = palette_group

        self._tsa_data = tsa_data

        self._images: dict[int, QImage] = {}

        if graphics_set.number == CLOUDY_GRAPHICS_SET:
            self._bg_color = NESPalette[palette_group[self._palette_index][2]]
        else:
            self._bg_color = NESPalette[palette_group[self._palette_index][0]]

        self._render()

    def _render(self):
        if self.graphics_set.anim_frame in self._images:
            return

        # can't hash list, so turn it into a string instead
        self._block_id: BlockId = (
            self.index,
            str(self._palette_group),
            self.graphics_set.number,
        )

        lu = self._tsa_data[TSA_BANK_0_START + self.index]
        ld = self._tsa_data[TSA_BANK_1_START + self.index]
        ru = self._tsa_data[TSA_BANK_2_START + self.index]
        rd = self._tsa_data[TSA_BANK_3_START + self.index]

        self.lu_tile = get_tile(lu, self._palette_group, self._palette_index, self.graphics_set)
        self.ld_tile = get_tile(ld, self._palette_group, self._palette_index, self.graphics_set)

        self.ru_tile = get_tile(ru, self._palette_group, self._palette_index, self.graphics_set)
        self.rd_tile = get_tile(rd, self._palette_group, self._palette_index, self.graphics_set)

        image = QImage(Block.WIDTH, Block.HEIGHT, QImage.Format_RGB888)

        painter = QPainter(image)

        painter.drawImage(QPoint(0, 0), self.lu_tile.as_image())
        painter.drawImage(QPoint(Tile.WIDTH, 0), self.ru_tile.as_image())
        painter.drawImage(QPoint(0, Tile.HEIGHT), self.ld_tile.as_image())
        painter.drawImage(QPoint(Tile.WIDTH, Tile.HEIGHT), self.rd_tile.as_image())

        painter.end()

        if _is_image_only_one_color(image) and image.pixelColor(0, 0) == QColor(*MASK_COLOR):
            self._whole_block_is_transparent = True
        else:
            self._whole_block_is_transparent = False

        self._images[self.graphics_set.anim_frame] = image

    def rerender(self):
        self._render()

    def draw(self, painter: QPainter, x, y, block_length, selected=False, transparent=False):
        block_attributes = (
            self._block_id,
            block_length,
            selected,
            transparent,
            self.graphics_set.anim_frame,
        )

        if block_attributes not in Block._block_cache:
            self.rerender()
            image = self._images[self.graphics_set.anim_frame].copy()

            if block_length != Block.WIDTH:
                image = image.scaled(block_length, block_length)

            # mask out the transparent pixels first
            mask = image.createMaskFromColor(QColor(*MASK_COLOR).rgb(), Qt.MaskMode.MaskOutColor)
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
        background.fill(self._bg_color)

        _painter = QPainter(background)
        _painter.drawImage(QPoint(), image)
        _painter.end()

        return background


def _is_image_only_one_color(image):
    copy = image.copy()

    copy.convertTo(QImage.Format_Indexed8)

    return copy.colorCount() == 1
