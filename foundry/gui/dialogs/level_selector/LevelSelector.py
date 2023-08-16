from typing import Optional

from PySide6.QtGui import QCloseEvent, QKeyEvent, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QGridLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
)

from foundry import icon
from foundry.game.File import ROM
from foundry.gui import OBJECT_SET_ITEMS
from foundry.gui.widgets.Spinner import Spinner
from smb3parse.data_points import LevelPointerData
from smb3parse.levels import WORLD_COUNT
from smb3parse.objects.object_set import (
    MUSHROOM_OBJECT_SET,
    SPADE_BONUS_OBJECT_SET,
    WORLD_MAP_OBJECT_SET,
)

from .found_level_list import FoundLevelWidget
from .overworld_selection_map import WorldMapLevelSelect
from .stock_level_list import StockLevelWidget


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

        self.clicked_level_pointer: Optional[LevelPointerData] = None

        self.enemy_data_label = QLabel(parent=self, text="Enemy Data")
        self.enemy_data_spinner = Spinner(parent=self)

        self.object_data_label = QLabel(parent=self, text="Object Data")
        self.object_data_spinner = Spinner(self)

        self.object_set_label = QLabel(parent=self, text="Object Set")
        self.object_set_dropdown = QComboBox(self)
        self.object_set_dropdown.addItems(OBJECT_SET_ITEMS)

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

        self._stock_level_widget.level_list.itemClicked.connect(self._on_stock_level_selected)

        self.source_selector.addTab(self._stock_level_widget, "Stock Levels")
        self.source_selector.setTabIcon(tab_index, icon("list.svg"))

        tab_index += 1

        if ROM.additional_data.found_levels:
            self._found_level_widget = FoundLevelWidget()
            self._found_level_widget.level_table.itemDoubleClicked.connect(self._on_ok)
            self._found_level_widget.level_table.itemSelectionChanged.connect(self._on_found_level_selected)

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

        data_layout = QGridLayout()

        data_layout.addWidget(self.enemy_data_label, 0, 0)
        data_layout.addWidget(self.object_data_label, 0, 1)
        data_layout.addWidget(self.enemy_data_spinner, 1, 0)
        data_layout.addWidget(self.object_data_spinner, 1, 1)

        data_layout.addWidget(self.object_set_label, 2, 0)
        data_layout.addWidget(self.object_set_dropdown, 2, 1)

        data_layout.addWidget(self.button_ok, 3, 0)
        data_layout.addWidget(self.button_cancel, 3, 1)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.source_selector)
        main_layout.addLayout(data_layout)

        self.setLayout(main_layout)

    def keyPressEvent(self, key_event: QKeyEvent):
        if key_event.key() == Qt.Key.Key_Escape:
            self.reject()

    def goto_world(self, world_number: int):
        if world_number not in range(1, WORLD_COUNT + 1):
            world_number = 1

        if ROM.additional_data.found_levels:
            world_number += 1

        self.source_selector.setCurrentIndex(world_number)

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
