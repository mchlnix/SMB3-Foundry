from typing import List

from PySide2.QtCore import QSize
from PySide2.QtGui import QColor, QPixmap
from PySide2.QtWidgets import QFrame, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from foundry.game.gfx.Palette import (
    COLORS_PER_PALETTE,
    PaletteController,
    PALETTES_PER_PALETTES_GROUP,
    PALETTE_GROUPS_PER_OBJECT_SET,
    load_palette,
)
from foundry.game.level.LevelRef import LevelRef
from foundry.gui.QDialog import Dialog


class PaletteViewer(Dialog):
    palettes_per_row = 4

    def __init__(self, parent, level_ref: LevelRef):
        title = f"Palette Groups for Object Set {level_ref.level.object_set_number}"

        super(PaletteViewer, self).__init__(parent, title=title)

        self.level_ref = level_ref

        layout = QGridLayout(self)

        for palette_group in range(PALETTE_GROUPS_PER_OBJECT_SET):
            group_box = QGroupBox()
            group_box.setTitle(f"Palette Group {palette_group}")

            group_box_layout = QVBoxLayout(group_box)
            group_box_layout.setSpacing(0)

            palette = load_palette(self.level_ref.level.object_set_number, palette_group)

            for palette_no in range(PALETTES_PER_PALETTES_GROUP):
                group_box_layout.addWidget(PaletteWidget(palette, palette_no))

            row = palette_group // self.palettes_per_row
            col = palette_group % self.palettes_per_row

            layout.addWidget(group_box, row, col)


class PaletteWidget(QWidget):
    def __init__(self, palette: List[bytearray], palette_number: int):
        super(PaletteWidget, self).__init__()

        layout = QHBoxLayout(self)

        for color_index in range(COLORS_PER_PALETTE):
            color = PaletteController().colors[palette[palette_number][color_index]]

            layout.addWidget(ColorSquare(color))

        for index in range(3, 0, -1):
            layout.insertStretch(index, 1)


class ColorSquare(QLabel):
    square_side_length = 16
    square_size = QSize(square_side_length, square_side_length)

    def __init__(self, color: QColor):
        super(ColorSquare, self).__init__()

        self.color = color

        color_square = QPixmap(self.square_size)
        color_square.fill(color)

        self.setPixmap(color_square)

        self.setFrameShape(QFrame.Box)
        self.setLineWidth(1)
