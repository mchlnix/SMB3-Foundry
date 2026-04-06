from PySide6.QtGui import QCloseEvent, QKeyEvent, QKeySequence, QShortcut, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
)

from foundry import get_level_thumbnail, icon
from foundry.game.File import ROM
from foundry.gui import OBJECT_SET_ITEMS
from foundry.gui.widgets.Spinner import Spinner
from smb3parse.constants import (
    MUSHROOM_OBJECT_SET,
    SPADE_BONUS_OBJECT_SET,
    WORLD_MAP_OBJECT_SET,
)
from smb3parse.data_points import LevelPointerData
from smb3parse.levels import HEADER_LENGTH, WORLD_COUNT
from smb3parse.levels.level_header import LevelHeader

from .found_level_list import FoundLevelWidget
from .overworld_selection_map import WorldMapLevelSelect
from .stock_level_list import StockLevelWidget


def _should_use_vertical_preview(level_address: int) -> bool:
    level_header_bytes = ROM().read(level_address, HEADER_LENGTH)

    level_header = LevelHeader(ROM(), level_header_bytes)

    return level_header.is_vertical or level_header.screens < 1


class _LevelPreviewWidget(QScrollArea):
    def __init__(self, vertical=False):
        super().__init__()

        self._is_vertical = vertical

        self._preview_label = QLabel()

        self.setWidget(self._preview_label)
        self.setWidgetResizable(True)

        # the scrollbars start with a default size of 100, 100, so adjust the size to get the real size here
        # see _push_out_scrollbars()
        self.verticalScrollBar().adjustSize()
        self.horizontalScrollBar().adjustSize()

    def set_level_preview(self, object_set_number: int, level_address: int, enemy_address: int):
        level_preview_pixmap = get_level_thumbnail(object_set_number, level_address, enemy_address)

        self._preview_label.setPixmap(level_preview_pixmap)
        self._preview_label.setFixedSize(level_preview_pixmap.size())

        self._push_out_scrollbars()

    def _push_out_scrollbars(self):
        """
        When the widget of a scroll area becomes to large, scrollbars are shown. Those are shown over the widget,
        however, without increasing the size of the scroll area. So if one scrollbar becomes necessary, its existence
        makes the other scrollbar also necessary. We forego that by extending the size of the widget by as many pixels
        as are needed for both the frame of the scroll area (linewidth) and the size of the scrollbar.
        """
        if self._is_vertical:
            self._push_out_vertical_scrollbar()

        if not self._is_vertical:
            self._push_out_horizontal_scrollbar()

    def _push_out_horizontal_scrollbar(self):
        new_height = self._preview_label.height() + self.lineWidth() * 2

        if self._preview_label.width() > self.width():
            new_height += self.horizontalScrollBar().height()

        self.setFixedHeight(new_height)

    def _push_out_vertical_scrollbar(self):
        new_width = self._preview_label.width() + self.lineWidth() * 2

        if self._preview_label.height() > self.height():
            new_width += self.verticalScrollBar().width()

        self.setFixedWidth(new_width)


class LevelSelector(QDialog):
    def __init__(self, parent):
        super(LevelSelector, self).__init__(parent)

        self.setWindowTitle("Level Selector")
        self.setModal(True)

        self.level_name = ""

        self.object_set = 0
        self.world_index = 0
        self.object_data_offset = 0x0
        self.enemy_data_offset = 0x0

        self.clicked_level_pointer: LevelPointerData | None = None

        self.enemy_data_label = QLabel(parent=self, text="Enemy Data")
        self.enemy_data_spinner = Spinner(parent=self)

        self.object_data_label = QLabel(parent=self, text="Object Data")
        self.object_data_spinner = Spinner(self)

        self.object_set_label = QLabel(parent=self, text="Object Set")
        self.object_set_dropdown = QComboBox(self)
        self.object_set_dropdown.addItems(OBJECT_SET_ITEMS)
        self.object_set_dropdown.currentTextChanged.connect(self._on_object_set_change)

        self.button_ok = QPushButton("Ok", self)
        self.button_ok.setEnabled(False)
        self.button_ok.clicked.connect(self._on_ok)
        self.button_ok.setFocus()

        self.button_cancel = QPushButton("Cancel", self)
        self.button_cancel.clicked.connect(self.close)

        # adding the tabs
        self.source_selector = QTabWidget()

        tab_index = 0

        self._stock_level_widget = StockLevelWidget()

        self._stock_level_widget.world_list.itemDoubleClicked.connect(self._on_ok)
        self._stock_level_widget.level_list.itemDoubleClicked.connect(self._on_ok)

        self._stock_level_widget.level_list.itemSelectionChanged.connect(self._on_stock_level_selected)

        self.source_selector.addTab(self._stock_level_widget, "Stock Levels")
        self.source_selector.setTabIcon(tab_index, icon("list.svg"))

        tab_index += 1

        if ROM.additional_data.found_levels:
            self._found_level_widget = FoundLevelWidget()
            self._found_level_widget.level_table.itemSelectionChanged.connect(self._on_found_level_selected)
            self._found_level_widget.level_table.itemDoubleClicked.connect(self._on_ok)

            self.source_selector.addTab(self._found_level_widget, "Found Levels")
            self.source_selector.setTabIcon(tab_index, icon("list.svg"))
            tab_index += 1

        for world_number in range(1, WORLD_COUNT):
            world_map_select = WorldMapLevelSelect(world_number)
            world_map_select.level_clicked.connect(self._on_level_selected_via_world_map)
            world_map_select.level_selected.connect(self._on_level_selected_via_world_map)
            world_map_select.level_selected.connect(self._on_ok)

            self.source_selector.addTab(world_map_select, f"World {world_number}")
            self.source_selector.setTabIcon(tab_index + world_number - 1, icon("globe.svg"))

        # show world 1 by default
        if self.source_selector.count() > tab_index:
            self.source_selector.setCurrentIndex(tab_index)

        # level previews
        self._horizontal_level_preview = _LevelPreviewWidget()
        self._horizontal_level_preview.hide()

        self._vertical_level_preview = _LevelPreviewWidget(vertical=True)
        self._vertical_level_preview.hide()

        data_layout = QGridLayout()

        data_layout.addWidget(self.enemy_data_label, 0, 0)
        data_layout.addWidget(self.object_data_label, 0, 1)
        data_layout.addWidget(self.enemy_data_spinner, 1, 0)
        data_layout.addWidget(self.object_data_spinner, 1, 1)

        data_layout.addWidget(self.object_set_label, 2, 0)
        data_layout.addWidget(self.object_set_dropdown, 2, 1)

        data_layout.addWidget(self.button_ok, 3, 0)
        data_layout.addWidget(self.button_cancel, 3, 1)

        selection_layout = QVBoxLayout()
        selection_layout.addWidget(self.source_selector)
        selection_layout.addWidget(self._horizontal_level_preview)
        selection_layout.addLayout(data_layout)

        main_layout = QHBoxLayout()
        main_layout.addLayout(selection_layout)
        main_layout.addWidget(self._vertical_level_preview)

        self.setLayout(main_layout)

        QShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_PageUp), self, self._one_tab_left)
        QShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_PageDown), self, self._one_tab_right)
        QShortcut(QKeySequence(Qt.Key.Key_Return), self, self._on_ok)
        QShortcut(QKeySequence(Qt.Key.Key_Enter), self, self._on_ok)

        if ROM.additional_data.found_levels:
            self._on_found_level_selected()
        else:
            self._on_stock_level_selected()

        # connect here, so we don't trigger the level preview on the automatically selected levels
        self.enemy_data_spinner.valueChanged.connect(self._update_level_preview)
        self.object_data_spinner.valueChanged.connect(self._update_level_preview)
        self.object_set_dropdown.currentTextChanged.connect(self._update_level_preview)

    def _one_tab_left(self):
        current_index = self.source_selector.currentIndex()
        tab_count = self.source_selector.count()

        new_index = (current_index - 1) % tab_count

        self.source_selector.setCurrentIndex(new_index)

    def _one_tab_right(self):
        current_index = self.source_selector.currentIndex()
        tab_count = self.source_selector.count()

        new_index = (current_index + 1) % tab_count

        self.source_selector.setCurrentIndex(new_index)

    def _on_object_set_change(self, _):
        self.button_ok.setEnabled(self.object_set_dropdown.currentIndex() != WORLD_MAP_OBJECT_SET)

    def keyPressEvent(self, key_event: QKeyEvent):
        if key_event.key() == Qt.Key.Key_Escape:
            self.reject()

    def goto_world(self, world_number: int):
        # default to world 1's tab
        tab_index = 1

        # if we got a valid world number, navigate to its tab
        if world_number in range(1, WORLD_COUNT + 1):
            tab_index = world_number

        if ROM.additional_data.found_levels:
            # if found levels are present, we added another tab in front of the world tabs
            tab_index += 1

        self.source_selector.setCurrentIndex(tab_index)

        self._stock_level_widget.world_number = world_number

    def deactivate_level_list(self):
        self.source_selector.setTabEnabled(0, False)

    def _on_stock_level_selected(self):
        self.world_index = self._stock_level_widget.world_number
        self.level_name = self._stock_level_widget.level_name

        self.enemy_data_spinner.setDisabled(self._stock_level_widget.level_is_overworld)
        self.button_ok.setDisabled(self._stock_level_widget.level_is_overworld)

        self._fill_in_data(
            self._stock_level_widget.object_set_number,
            self._stock_level_widget.level_address,
            self._stock_level_widget.enemy_address,
        )

    def _fill_in_data(self, object_set: int, layout_address: int, enemy_address: int):
        self.object_set_dropdown.setCurrentIndex(object_set)
        self.object_data_spinner.setValue(layout_address)
        self.enemy_data_spinner.setValue(enemy_address)

    def _update_level_preview(self):
        self._horizontal_level_preview.hide()
        self._vertical_level_preview.hide()

        object_set = self.object_set_dropdown.currentIndex()
        layout_address = self.object_data_spinner.value()
        enemy_address = self.enemy_data_spinner.value()

        if object_set in [WORLD_MAP_OBJECT_SET, MUSHROOM_OBJECT_SET, SPADE_BONUS_OBJECT_SET]:
            return

        if _should_use_vertical_preview(layout_address):
            preview_widget = self._vertical_level_preview
        else:
            preview_widget = self._horizontal_level_preview

        preview_widget.set_level_preview(object_set, layout_address, enemy_address)
        preview_widget.show()

    def _on_level_selected_via_world_map(self, level_name: str, level_pointer: LevelPointerData):
        self.level_name = level_name

        if self.clicked_level_pointer == level_pointer:
            # same level was clicked again,
            self._on_ok()
        else:
            self.clicked_level_pointer = level_pointer

        self.world_index = level_pointer.world.index + 1

        self._fill_in_data(
            level_pointer.object_set,
            level_pointer.level_address,
            level_pointer.enemy_address,
        )

        self.button_ok.setEnabled(True)
        self.button_ok.setFocus()

    def _on_found_level_selected(self):
        self._fill_in_data(
            self._found_level_widget.object_set_number,
            self._found_level_widget.level_address,
            self._found_level_widget.enemy_address,
        )

        self.world_index = self._found_level_widget.world_number

        self.button_ok.setEnabled(True)
        self.button_ok.setFocus()

    def _on_ok(self, _=None):
        if self.object_set_dropdown.currentIndex() == WORLD_MAP_OBJECT_SET:
            return

        if self.object_set_dropdown.currentIndex() in (MUSHROOM_OBJECT_SET, SPADE_BONUS_OBJECT_SET):
            QMessageBox.warning(
                self,
                "No can do",
                "Spade and mushroom house levels are currently not supported, and can't be edited.",
            )
            return

        self.object_set = self.object_set_dropdown.currentIndex()
        self.object_data_offset = self.object_data_spinner.value()
        self.enemy_data_offset = self.enemy_data_spinner.value()

        self.accept()

    def closeEvent(self, _close_event: QCloseEvent):
        self.reject()
