from PySide2.QtCore import QSize
from PySide2.QtGui import QColor, QPixmap
from PySide2.QtWidgets import QFrame, QGroupBox, QHBoxLayout, QLabel, QVBoxLayout

from foundry.game.gfx.Palette import (
    COLORS_PER_PALETTE,
    LEVEL_PALETTE_GROUPS_PER_OBJECT_SET,
    NESPalette,
    PALETTES_PER_PALETTES_GROUP,
    load_palette,
)
from foundry.game.level.LevelRef import LevelRef
from foundry.gui.CustomDialog import CustomDialog


class PaletteViewer(CustomDialog):
    def __init__(self, parent, level_ref: LevelRef):
        title = f"Palette Groups for Object set {level_ref.level.object_set_number}"

        super(PaletteViewer, self).__init__(parent, title=title)

        self.level_ref = level_ref

        layout = QVBoxLayout(self)

        for palette_group in range(LEVEL_PALETTE_GROUPS_PER_OBJECT_SET):
            group_box = QGroupBox()
            group_box.setTitle(f"Object Palette Group {palette_group}")
            group_box_layout = QHBoxLayout()
            group_box.setLayout(group_box_layout)

            palette = load_palette(self.level_ref.level.object_set_number, palette_group)

            for palette_no in range(PALETTES_PER_PALETTES_GROUP):
                for color_index in range(COLORS_PER_PALETTE):
                    color = QColor(*NESPalette[palette[palette_no][color_index]])

                    group_box_layout.addWidget(ColorSquare(color))

                if palette_no < PALETTES_PER_PALETTES_GROUP - 1:
                    # don't put spacing after the last palette
                    group_box_layout.addSpacing(10)

            layout.addWidget(group_box)


class ColorSquare(QLabel):
    def __init__(self, color: QColor):
        super(ColorSquare, self).__init__()

        self.color = color

        color_square = QPixmap(QSize(32, 32))
        color_square.fill(color)

        self.setPixmap(color_square)

        self.setFrameShape(QFrame.Box)
        self.setLineWidth(1)
