from random import randint, seed

from PySide6.QtGui import QColor, QPaintEvent, QPainter, Qt
from PySide6.QtWidgets import QTabWidget, QWidget

from foundry.game.File import ROM
from foundry.gui.CustomChildWindow import CustomChildWindow
from smb3parse.constants import PAGE_A000_ByTileset
from smb3parse.objects.object_set import ENEMY_ITEM_OBJECT_SET, PLAINS_OBJECT_SET, SPADE_BONUS_OBJECT_SET
from smb3parse.util.parser.level import ParsedLevel


class LevelViewer(CustomChildWindow):
    def __init__(
        self, parent, addresses_by_object_set: dict[int, list[int]], levels_by_address: dict[int, ParsedLevel]
    ):
        super(LevelViewer, self).__init__(parent, "Level Viewer")

        self.addresses_by_object_set = addresses_by_object_set
        self.levels_by_address = levels_by_address

        prg_banks_by_object_set = ROM().read(PAGE_A000_ByTileset, 16)

        # get connection between PRG bank and object set
        prg_banks = list(set(prg_banks_by_object_set[PLAINS_OBJECT_SET:SPADE_BONUS_OBJECT_SET]))
        prg_banks.sort()

        self._tab_widget = QTabWidget(self)

        self.setCentralWidget(self._tab_widget)

        for prg in prg_banks:
            self._tab_widget.addTab(ByteView([]), f"PRG #{prg}")

        for address in sorted(levels_by_address.keys()):
            level = levels_by_address[address]
            tab_index = prg_banks.index(prg_banks_by_object_set[level.object_set_num])

            byte_view = self._tab_widget.widget(tab_index)
            byte_view.levels_in_order.append((level.object_set_num - 1, address, level.length))


class ByteView(QWidget):
    def __init__(self, levels_in_order: list[tuple[int, int, int]]):
        super(ByteView, self).__init__()

        self.levels_in_order = levels_in_order
        seed(0)
        self._random_colors = [
            QColor(randint(0, 255), randint(0, 255), randint(0, 255)) for _ in range(ENEMY_ITEM_OBJECT_SET)
        ]

    def paintEvent(self, event: QPaintEvent):
        if not self.levels_in_order:
            return

        painter = QPainter(self)

        byte_side_length = 8

        width = self.width() // byte_side_length
        height = self.height() // byte_side_length

        start = self.levels_in_order[0][1]

        for object_set, level_start, level_length in self.levels_in_order:
            color = self._random_colors[object_set]

            level_start -= start

            for level_byte in range(level_length):
                cur_pos = level_start + level_byte
                x = (cur_pos % width) * byte_side_length
                y = (cur_pos // width) * byte_side_length

                painter.fillRect(x, y, byte_side_length, byte_side_length, color)

        painter.setPen(Qt.black)

        for x in range(1, width):
            x *= byte_side_length

            painter.drawLine(x, 0, x, self.height())

        for y in range(1, height):
            y *= byte_side_length

            painter.drawLine(0, y, self.width(), y)
