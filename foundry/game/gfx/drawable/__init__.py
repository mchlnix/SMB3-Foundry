from PySide6.QtCore import QPoint, QRect
from PySide6.QtGui import QColor, QImage, QPainter, Qt

from foundry import data_dir

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


def load_from_object_sprite_sheet(x: int, y: int):
    sprite_side_length = 16

    cut_out_area = QRect(*(Rect(x, y, 1, 1) * sprite_side_length))
    image = OBJECT_SPRITE_SHEET.copy(cut_out_area)

    mask = image.createMaskFromColor(QColor(*MASK_COLOR).rgb(), Qt.MaskMode.MaskOutColor)
    image.setAlphaChannel(mask)

    return image


def apply_selection_overlay(image, mask):
    overlay = image.copy()
    overlay.fill(SELECTION_OVERLAY_COLOR)
    overlay.setAlphaChannel(mask)

    _painter = QPainter(image)
    _painter.drawImage(QPoint(), overlay)
    _painter.end()
