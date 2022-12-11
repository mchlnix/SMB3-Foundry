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

from foundry.game.File import ROM
from foundry.game.gfx.Palette import (
    COLORS_PER_PALETTE,
    NESPalette,
    PALETTES_PER_PALETTES_GROUP,
    PALETTE_GROUPS_PER_OBJECT_SET,
    load_palette_group,
)
from foundry.game.gfx import change_color
from foundry.game.level.LevelRef import LevelRef
from foundry.gui.CustomDialog import CustomDialog
from foundry.gui.commands import UpdatePalette


class PaletteViewer(CustomDialog):
    palettes_per_row = 4

    def __init__(self, parent, level_ref: LevelRef):
        title = f"Palette Groups for Object Set {level_ref.level.object_set_number}"

        super(PaletteViewer, self).__init__(parent, title=title)

        self.level_ref = level_ref

        layout = QGridLayout(self)

        for palette_group_number in range(PALETTE_GROUPS_PER_OBJECT_SET):
            group_box = QGroupBox()
            group_box.setTitle(f"Palette Group {palette_group_number}")

            group_box_layout = QVBoxLayout(group_box)
            group_box_layout.setSpacing(0)

            for palette_no in range(PALETTES_PER_PALETTES_GROUP):
                group_box_layout.addWidget(PaletteWidget(level_ref, palette_group_number, palette_no))

            row = palette_group_number // self.palettes_per_row
            col = palette_group_number % self.palettes_per_row

            layout.addWidget(group_box, row, col)


class PaletteWidget(QWidget):
    # index in palette, color index in NES palette
    color_changed: SignalInstance = Signal(int, int)
    color_committed: SignalInstance = Signal(int, int)

    def __init__(self, level_ref: LevelRef, group_number: int, palette_number: int):
        super(PaletteWidget, self).__init__()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(1, 2, 0, 2)

        self.level_ref = level_ref
        self.group_number = group_number
        self._palette_number = palette_number

        self.clickable = False

        self._color_squares = []

        for color_index in range(COLORS_PER_PALETTE):
            square = ColorSquare()
            square.clicked.connect(self._open_color_table)

            self._color_squares.append(square)

            layout.addWidget(square)

        self._update_colors()

    @property
    def _palette_group(self):
        return load_palette_group(self.level_ref.level.object_set_number, self.group_number)

    def update(self):
        self._update_colors()

    def _open_color_table(self):
        if not self.clickable:
            return

        index_in_palette = self.layout().indexOf(self.sender())
        original_color_index = self.sender().color_index

        color_table = ColorTable()
        color_table.color_clicked.connect(lambda x: self.color_changed.emit(index_in_palette, x))
        color_table.color_clicked.connect(self._update_colors)

        answer = color_table.exec()

        self.color_changed.emit(index_in_palette, original_color_index)

        if answer == QDialog.Accepted:
            if color_table.selected_color_index != original_color_index:
                self.color_committed.emit(index_in_palette, color_table.selected_color_index)

        self._update_colors()

    def _update_colors(self):
        for color_index, color_square in zip(self._palette_group[self._palette_number], self._color_squares):
            color_square.set_color(color_index)


class ColorSquare(QLabel):
    clicked: SignalInstance = Signal()

    def __init__(self, color_index=-1, square_length=16):
        super(ColorSquare, self).__init__()

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.square_size = QSize(square_length, square_length)

        self._set_color(color_index)

    def _set_color(self, color_index: int):
        self.color_index = color_index

        if color_index != -1:
            color = NESPalette[color_index]
        else:
            color = QColor(Qt.white)

        self.color = color
        color_square = QPixmap(self.square_size)
        color_square.fill(color)

        self.setPixmap(color_square)

        self.select(False)

    def set_color(self, color_index: int):
        self._set_color(color_index)
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

    color_clicked: SignalInstance = Signal(int)
    ok_clicked: SignalInstance = Signal(int)

    def __init__(self):
        super(ColorTable, self).__init__()

        self.setWindowTitle("NES Color Table")

        self._currently_selected_square: ColorSquare = ColorSquare()
        self.selected_color_index = 0
        """Index into the NES Palette, that was selected."""

        self.square_length = 24

        self.color_table_layout = QGridLayout()
        self.color_table_layout.setSpacing(0)

        for row, column in product(range(self.table_rows), range(self.table_columns)):
            color_index = row * self.table_columns + column

            square = ColorSquare(color_index, self.square_length)
            square.setLineWidth(0)

            square.clicked.connect(self._on_click)

            self.color_table_layout.addWidget(square, row, column)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.buttons.clicked.connect(self._on_button)

        layout = QVBoxLayout(self)
        layout.addLayout(self.color_table_layout)

        layout.addWidget(self.buttons, alignment=Qt.AlignCenter)

    def _on_click(self):
        color_index = self.sender().color_index
        self.select_square(self.sender())
        self.color_clicked.emit(color_index)

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

        self._palette_widgets: list[PaletteWidget] = []

        self.update()

        self.setWhatsThis(
            "<b>Object Palettes</b><br/>"
            "This shows the current palette group of the level, which can be changed in the level header "
            "editor.<br/>"
            "By clicking on the individual colors, you can change them.<br/><br/>"
            ""
            "Note: The first color (the left most one) is always the same among all 4 palettes."
        )

    @property
    def palette_group(self):
        return load_palette_group(self.level_ref.object_set_number, self.level_ref.object_palette_index)

    @property
    def undo_stack(self) -> QUndoStack:
        return self.parent().window().findChild(QUndoStack, "undo_stack")

    def _setup(self):
        for palette_no in range(PALETTES_PER_PALETTES_GROUP):
            widget = PaletteWidget(self.level_ref, self.level_ref.object_palette_index, palette_no)
            widget.color_changed.connect(self.on_color_change(palette_no))
            widget.color_committed.connect(self.on_color_commit(palette_no))
            widget.clickable = True

            self.layout().addWidget(widget)
            self._palette_widgets.append(widget)

    def update(self):
        if self.layout().isEmpty() and ROM.is_loaded() and self.level_ref:
            self._setup()

        for widget in self._palette_widgets:
            widget.group_number = self.level_ref.level.header.object_palette_index
            widget.update()

    def on_color_change(self, palette_no: int) -> Callable:
        def actual_changer(index_in_palette, index_in_nes_color_table):
            change_color(self.palette_group, palette_no, index_in_palette, index_in_nes_color_table)

            self.level_ref.level.reload()

        return actual_changer

    def on_color_commit(self, palette_no: int) -> Callable:
        def actual_commiter(index_in_palette, index_in_nes_color_table):
            self.undo_stack.push(
                UpdatePalette(
                    self.level_ref, self.palette_group, palette_no, index_in_palette, index_in_nes_color_table
                )
            )

        return actual_commiter
