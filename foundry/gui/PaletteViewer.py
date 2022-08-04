from itertools import product
from typing import Callable

from PySide6.QtCore import QSize, Signal, SignalInstance
from PySide6.QtGui import QColor, QMouseEvent, QPixmap, QUndoStack, Qt
from PySide6.QtWidgets import (
    QAbstractButton,
    QDialog,
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
    PaletteGroup,
    load_palette_group,
)
from foundry.game.level.LevelRef import LevelRef
from foundry.gui.CustomDialog import CustomDialog
from foundry.gui.commands import UpdatePalette
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
    # index in palette, color index in NES palette
    color_changed: SignalInstance = Signal(int, int)

    def __init__(self, palette_group: PaletteGroup, palette_number: int):
        super(PaletteWidget, self).__init__()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(1, 2, 0, 2)

        self._palette_group = palette_group
        self._palette_number = palette_number

        self.clickable = False

        self._color_squares = []

        for color_index in range(COLORS_PER_PALETTE):
            square = ColorSquare()
            square.clicked.connect(self._open_color_table)

            self._color_squares.append(square)

            layout.addWidget(square)

        self._update_colors()

    def _open_color_table(self):
        if not self.clickable:
            return

        color_table = ColorTable()
        return_code = color_table.exec()

        if return_code == QDialog.Accepted:
            index_in_palette = self.layout().indexOf(self.sender())
            color_in_nes_palette = color_table.selected_color_index

            self.color_changed.emit(index_in_palette, color_in_nes_palette)

            self._update_colors()

    def _update_colors(self):
        for color_index, color_square in zip(self._palette_group[self._palette_number], self._color_squares):
            color = NESPalette[color_index]

            color_square.set_color(color)


class ColorSquare(QLabel):
    clicked: SignalInstance = Signal()

    def __init__(self, color: QColor = QColor(Qt.white), square_length=16):
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

    def set_color(self, color: QColor):
        self._set_color(color)
        self.update()

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


class ColorTable(QDialog):
    table_rows = 4
    table_columns = 16

    ok_clicked: SignalInstance = Signal(int)

    def __init__(self):
        super(ColorTable, self).__init__()

        self.setWindowTitle("NES Color Table")

        self._currently_selected_square: ColorSquare = ColorSquare(QColor(Qt.white))
        self.selected_color_index = 0
        """Index into the NES Palette, that was selected."""

        self.square_length = 24

        self.color_table_layout = QGridLayout()
        self.color_table_layout.setSpacing(0)

        for row, column in product(range(self.table_rows), range(self.table_columns)):
            color = NESPalette[row * self.table_columns + column]

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

            self.selected_color_index = color_index
            self.accept()
        else:
            self.reject()


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

    @property
    def undo_stack(self) -> QUndoStack:
        return self.parent().window().findChild(QUndoStack, "undo_stack")

    def update(self):
        clear_layout(self.layout())

        palette_group_index = self.level_ref.object_palette_index
        palette_group = load_palette_group(self.level_ref.object_set_number, palette_group_index)

        for palette_no in range(PALETTES_PER_PALETTES_GROUP):
            widget = PaletteWidget(palette_group, palette_no)
            widget.color_changed.connect(self.color_changer(palette_group, palette_no))
            widget.clickable = True

            self.layout().addWidget(widget)

    def color_changer(self, palette_group: PaletteGroup, palette_no: int) -> Callable:
        def actual_changer(index_in_palette, index_in_nes_color_table):
            palette = palette_group[palette_no]
            if palette[index_in_palette] == index_in_nes_color_table:
                return

            self.undo_stack.push(
                UpdatePalette(self.level_ref, palette_group, palette_no, index_in_palette, index_in_nes_color_table)
            )

            self.level_ref.reload()

        return actual_changer
