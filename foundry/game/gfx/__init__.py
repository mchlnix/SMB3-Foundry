from PySide6.QtCore import QSize
from PySide6.QtGui import QColor, QImage, QPainter

from foundry.game.gfx.block_cache import BlockCache, draw_enemy_item, draw_level_object
from foundry.game.gfx.drawable.Block import Block
from foundry.game.gfx.GraphicsSet import GraphicsSet
from foundry.game.gfx.objects.in_level.enemy_item import EnemyItem
from foundry.game.gfx.objects.in_level.in_level_object import InLevelObject
from foundry.game.gfx.objects.in_level.level_object import LevelObject
from foundry.game.gfx.Palette import (
    PaletteGroup,
    _palette_group_cache,
    bg_color_for_object_set,
)


def restore_all_palettes():
    """Restore all palettes.

    It supports palette, graphics, and block data used by the editor rendering pipeline. The method updates stored state that later editor operations depend on.
    """
    for palette_group in _palette_group_cache.values():
        palette_group.restore()

    BlockCache.clear_cache()
    Block.clear_cache()
    PaletteGroup.changed = False


def restore_graphics():
    """Restore graphics.

    It supports palette, graphics, and block data used by the editor rendering pipeline. The method delegates lower-level work while keeping the public workflow focused.
    """
    GraphicsSet.from_number.cache_clear()
    restore_all_palettes()


def change_color(
    palette_group: PaletteGroup,
    index_in_group: int,
    index_in_palette: int,
    new_color_index: int,
):
    # colors at index 0 are shared among all palettes of a palette group
    """Change color.

    It supports palette, graphics, and block data used by the editor rendering pipeline. The method delegates lower-level work while keeping the public workflow focused.

    Parameters
    ----------
    palette_group : PaletteGroup
        Palette group used for drawing the object.
    index_in_group : int
        Index in group used by the operation.
    index_in_palette : int
        Index in palette used by the operation.
    new_color_index : int
        Index of the new color.
    """
    if index_in_palette == 0:
        for palette_ in palette_group._palettes:
            palette_[0] = new_color_index
    else:
        palette_group[index_in_group][index_in_palette] = new_color_index

    BlockCache.clear_cache()


def object_to_image(obj: "InLevelObject"):
    """Return to image.

    It supports palette, graphics, and block data used by the editor rendering pipeline. The drawing path keeps rendering decisions close to the model state it displays.

    Parameters
    ----------
    obj : 'InLevelObject'
        Object being inspected or modified.

    Returns
    -------
    Any
        Rendered image for the object.
    """
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

        draw_level_object(obj, painter, Block.SIDE_LENGTH, True, False)

        return image

    else:
        assert isinstance(obj, EnemyItem)

        image = QImage(
            QSize(obj.width * Block.SIDE_LENGTH, obj.height * Block.SIDE_LENGTH),
            QImage.Format.Format_RGBA8888,
        )

        image.fill(QColor(0, 0, 0, 0))

        painter = QPainter(image)

        draw_enemy_item(obj, painter, Block.SIDE_LENGTH, False)

        return image
