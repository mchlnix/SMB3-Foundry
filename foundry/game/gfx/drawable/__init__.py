from PySide6.QtCore import QPoint, QRect
from PySide6.QtGui import QColor, QImage, QPainter, Qt

from foundry import data_dir
from smb3parse.constants import (
    POWERUP_FIREFLOWER,
    POWERUP_FROG,
    POWERUP_HAMMER,
    POWERUP_MUSHROOM,
    POWERUP_NONE,
    POWERUP_RACCOON,
    POWERUP_TANOOKI,
)
from smb3parse.util.rect import Rect

MASK_COLOR = [0xFF, 0x00, 0xFF]

SELECTION_OVERLAY_COLOR = QColor(20, 87, 159, 80)

OBJECT_SPRITE_SHEET = QImage(str(data_dir / "gfx.png"))
OBJECT_SPRITE_SHEET.convertTo(QImage.Format.Format_RGB888)

_mario_sprite_dir = data_dir / "mario_sprites"

MARIO_SPRITE_SHEET_BY_POWERUP = {
    POWERUP_NONE: QImage(str(_mario_sprite_dir / "mario-small.png")),
    POWERUP_MUSHROOM: QImage(str(_mario_sprite_dir / "mario-big.png")),
    POWERUP_FIREFLOWER: QImage(str(_mario_sprite_dir / "mario-fire.png")),
    POWERUP_RACCOON: QImage(str(_mario_sprite_dir / "mario-raccoon.png")),
    POWERUP_FROG: QImage(str(_mario_sprite_dir / "mario-frog.png")),
    POWERUP_TANOOKI: QImage(str(_mario_sprite_dir / "mario-tanooki.png")),
    POWERUP_HAMMER: QImage(str(_mario_sprite_dir / "mario-hammer.png")),
}


def make_image_selected(image: QImage) -> QImage:
    """Return a copy of an image with the editor selection overlay applied.

    Parameters
    ----------
    image : QImage
        Source image whose existing alpha mask defines the selected pixels.

    Returns
    -------
    QImage
        Selected copy of ``image``.
    """
    alpha_mask = image.createAlphaMask()
    alpha_mask.invertPixels()

    selected_image = QImage(image)

    apply_selection_overlay(selected_image, alpha_mask)

    return selected_image


def load_from_object_sprite_sheet(x: int, y: int):
    """Load a 16x16 preview sprite from the object sprite sheet.

    Parameters
    ----------
    x : int
        Tile column in the sprite sheet.
    y : int
        Tile row in the sprite sheet.

    Returns
    -------
    QImage
        Sprite image with ``MASK_COLOR`` pixels converted to transparency.
    """
    sprite_side_length = 16

    cut_out_area = QRect(*(Rect(x, y, 1, 1) * sprite_side_length))
    image = OBJECT_SPRITE_SHEET.copy(cut_out_area)

    mask = image.createMaskFromColor(QColor(*MASK_COLOR).rgb(), Qt.MaskMode.MaskOutColor)
    image.setAlphaChannel(mask)

    return image


def apply_selection_overlay(image, mask):
    """Paint the editor selection tint through an alpha mask.

    Parameters
    ----------
    image : QImage
        Image to modify in place.
    mask : QImage
        Alpha mask limiting where the selection tint is painted.
    """
    overlay = image.copy()
    overlay.fill(SELECTION_OVERLAY_COLOR)
    overlay.setAlphaChannel(mask)

    _painter = QPainter(image)
    _painter.drawImage(QPoint(), overlay)
    _painter.end()
