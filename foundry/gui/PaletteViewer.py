from itertools import product
from typing import List

from PySide2.QtCore import QSize, Signal, SignalInstance
from PySide2.QtGui import QColor, QMouseEvent, QPixmap, Qt
from PySide2.QtWidgets import (
    QAbstractButton,
    QDialogButtonBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from foundry.game.gfx.Palette import (
    COLORS_PER_PALETTE,
    NESPalette,
    PALETTES_PER_PALETTES_GROUP,
    PALETTE_GROUPS_PER_OBJECT_SET,
    load_palette_group,
)
from foundry.game.level.LevelRef import LevelRef
from foundry.gui.CustomDialog import CustomDialog
from foundry.gui.util import clear_layout


class PaletteViewer(CustomDialog):
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

            palette = load_palette_group(self.level_ref.level.object_set_number, palette_group)

            for palette_no in range(PALETTES_PER_PALETTES_GROUP):
                group_box_layout.addWidget(PaletteWidget(palette, palette_no))

            row = palette_group // self.palettes_per_row
            col = palette_group % self.palettes_per_row

            layout.addWidget(group_box, row, col)


class PaletteWidget(QWidget):
    def __init__(self, palette: List[bytearray], palette_number: int):
        super(PaletteWidget, self).__init__()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(1, 2, 0, 2)

        for color_index in range(COLORS_PER_PALETTE):
            color = QColor(*NESPalette[palette[palette_number][color_index]])

            square = ColorSquare(color)
            square.clicked.connect(self._open_color_table)

            layout.addWidget(square)

    def _open_color_table(self):
        pass


class ColorSquare(QLabel):
    clicked: SignalInstance = Signal()

    def __init__(self, color: QColor, square_length=16):
        super(ColorSquare, self).__init__()

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.square_size = QSize(square_length, square_length)

        self._set_color(color)

    def _set_color(self, color: QColor):
        self.color = color
        color_square = QPixmap(self.square_size)
        color_square.fill(color)

        self.setPixmap(color_square)

        self.select(False)

    def select(self, selected):
        if selected:
            if self.color.lightnessF() < 0.25:
                self.setStyleSheet("border-color: rgb(255, 255, 255); border-width: 2px; border-style: solid")
            else:
                self.setStyleSheet("border-color: rgb(0, 0, 0); border-width: 2px; border-style: solid")
        else:
            rgb = self.color.getRgb()
            self.setStyleSheet(
                f"border-color: rgb({rgb[0]}, {rgb[1]}, {rgb[2]}); border-width: 2px; border-style: solid"
            )

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.clicked.emit()

        return super(ColorSquare, self).mouseReleaseEvent(event)


class ColorTable(QWidget):
    table_rows = 4
    table_columns = 16

    ok_clicked: SignalInstance = Signal(int)

    def __init__(self):
        super(ColorTable, self).__init__()

        self.setWindowTitle("NES Color Table")

        self._currently_selected_square: ColorSquare = ColorSquare(QColor(Qt.white))

        self.square_length = 24

        self.color_table_layout = QGridLayout()
        self.color_table_layout.setSpacing(0)

        for row, column in product(range(self.table_rows), range(self.table_columns)):
            color = QColor(*NESPalette[row * self.table_columns + column])

            square = ColorSquare(color, self.square_length)
            square.setLineWidth(0)

            square.clicked.connect(self._on_click)

            self.color_table_layout.addWidget(square, row, column)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.buttons.clicked.connect(self._on_button)

        layout = QVBoxLayout(self)
        layout.addLayout(self.color_table_layout)

        layout.addWidget(self.buttons, alignment=Qt.AlignCenter)

    def _on_click(self):
        self.select_square(self.sender())

    def select_square(self, color_square: ColorSquare):
        self._currently_selected_square.select(False)

        color_square.select(True)

        self._currently_selected_square = color_square

    def _on_button(self, button: QAbstractButton):
        if button is self.buttons.button(QDialogButtonBox.Ok):  # ok button
            color_index = self.color_table_layout.indexOf(self._currently_selected_square)

            self.ok_clicked.emit(color_index)

        self.close()


class SidePalette(QWidget):
    def __init__(self, level_ref: LevelRef):
        super(SidePalette, self).__init__()

        self.level_ref = level_ref

        self.level_ref.data_changed.connect(self.update)

        self.setLayout(QVBoxLayout(self))
        self.layout().setSpacing(0)

        self.setWhatsThis(
            "<b>Object Palettes</b><br/>"
            "This shows the current palette group of the level, which can be changed in the level header "
            "editor.<br/>"
            "By clicking on the individual colors, you can change them.<br/><br/>"
            ""
            "Note: The first color (the left most one) is always the same among all 4 palettes."
        )

    def update(self):
        clear_layout(self.layout())

        palette_group_index = self.level_ref.object_palette_index
        palette = load_palette_group(self.level_ref.object_set_number, palette_group_index)

        for palette_no in range(PALETTES_PER_PALETTES_GROUP):
            self.layout().addWidget(PaletteWidget(palette, palette_no))
