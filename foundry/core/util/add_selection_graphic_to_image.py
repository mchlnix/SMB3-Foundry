from PySide2.QtGui import QImage

from foundry.game.gfx.drawable import apply_selection_overlay


def add_selection_graphic_to_image(image: QImage) -> QImage:
    alpha_mask = image.createAlphaMask()
    alpha_mask.invertPixels()

    selected_image = QImage(image)

    apply_selection_overlay(selected_image, alpha_mask)

    return selected_image