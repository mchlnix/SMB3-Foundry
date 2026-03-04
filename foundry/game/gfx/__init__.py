from PySide6.QtCore import QSize
from PySide6.QtGui import QImage, QPainter

from foundry.game.gfx.block_cache import BlockCache, draw_level_object
from foundry.game.gfx.drawable.Block import Block, get_tile
from foundry.game.gfx.GraphicsSet import GraphicsSet
from foundry.game.gfx.objects.in_level.in_level_object import InLevelObject
from foundry.game.gfx.objects.in_level.level_object import LevelObject
from foundry.game.gfx.Palette import (
    PaletteGroup,
    _palette_group_cache,
    bg_color_for_object_set,
)


def restore_all_palettes():
    for palette_group in _palette_group_cache.values():
        palette_group.restore()

    get_tile.cache_clear()
    BlockCache.clear_cache()
    Block.clear_cache()
    PaletteGroup.changed = False


def restore_graphics():
    GraphicsSet.from_number.cache_clear()
    restore_all_palettes()


def change_color(
    palette_group: PaletteGroup,
    index_in_group: int,
    index_in_palette: int,
    new_color_index: int,
):
    # colors at index 0 are shared among all palettes of a palette group
    if index_in_palette == 0:
        for palette_ in palette_group._palettes:
            palette_[0] = new_color_index
    else:
        palette_group[index_in_group][index_in_palette] = new_color_index

    get_tile.cache_clear()
    BlockCache.clear_cache()


def object_to_image(obj: "InLevelObject"):
    if isinstance(obj, LevelObject):
        obj.rendered_base_x = 0
        obj.rendered_base_y = 0

        image = QImage(
            QSize(
                obj.rendered_width * Block.SIDE_LENGTH,
                obj.rendered_height * Block.SIDE_LENGTH,
            ),
            QImage.Format.Format_RGB888,
        )

        bg_color = bg_color_for_object_set(obj.object_set.number, 0)

        image.fill(bg_color)

        painter = QPainter(image)

        draw_level_object(obj, painter, Block.SIDE_LENGTH, True)

        return image

    return obj.as_image()
