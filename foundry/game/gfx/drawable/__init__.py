from typing import TYPE_CHECKING

from PySide6.QtCore import QPoint, QRect, QSize
from PySide6.QtGui import QColor, QImage, QPainter, Qt

from foundry import data_dir
from foundry.game.gfx.block_cache import draw_level_object
from foundry.game.gfx.Palette import bg_color_for_object_set

if TYPE_CHECKING:
    from foundry.game.gfx.objects.in_level.in_level_object import InLevelObject

MASK_COLOR = [0xFF, 0x00, 0xFF]

SELECTION_OVERLAY_COLOR = QColor(20, 87, 159, 80)

png = QImage(str(data_dir / "gfx.png"))
png.convertTo(QImage.Format.Format_RGB888)

mario_actions = QImage(str(data_dir / "mario.png"))
mario_actions.convertTo(QImage.Format.Format_RGBA8888)


def make_image_selected(image: QImage) -> QImage:
    alpha_mask = image.createAlphaMask()
    alpha_mask.invertPixels()

    selected_image = QImage(image)

    apply_selection_overlay(selected_image, alpha_mask)

    return selected_image


def load_from_png(x: int, y: int):
    image = png.copy(QRect(x * 16, y * 16, 16, 16))
    mask = image.createMaskFromColor(QColor(*MASK_COLOR).rgb(), Qt.MaskMode.MaskOutColor)
    image.setAlphaChannel(mask)

    return image


def object_to_image(obj: "InLevelObject"):
    from foundry.game.gfx.drawable.Block import Block
    from foundry.game.gfx.objects import LevelObject

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


def apply_selection_overlay(image, mask):
    overlay = image.copy()
    overlay.fill(SELECTION_OVERLAY_COLOR)
    overlay.setAlphaChannel(mask)

    _painter = QPainter(image)
    _painter.drawImage(QPoint(), overlay)
    _painter.end()
