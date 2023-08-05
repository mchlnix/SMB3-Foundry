from contextlib import suppress
from typing import Optional

from PySide6.QtCore import QMargins, QSize, Signal, SignalInstance
from PySide6.QtGui import QCloseEvent, QKeyEvent, QMouseEvent, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QGridLayout,
    QLabel,
    QListWidget,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QScrollBar,
    QSizePolicy,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from foundry import icon
from foundry.game.File import ROM
from foundry.game.level.LevelRef import LevelRef
from foundry.game.level.WorldMap import WorldMap
from foundry.gui import OBJECT_SET_ITEMS
from foundry.gui.WorldView import WorldView
from foundry.gui.dialogs.level_selector.stock_level_list import StockLevelWidget
from foundry.gui.settings import Settings
from foundry.gui.widgets.Spinner import Spinner
from smb3parse.data_points import LevelPointerData, Position
from smb3parse.levels import WORLD_COUNT
from smb3parse.objects.object_set import (
    MUSHROOM_OBJECT_SET,
    OBJECT_SET_NAMES,
    SPADE_BONUS_OBJECT_SET,
    WORLD_MAP_OBJECT_SET,
)


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

        self._stock_level_widget = StockLevelWidget()

        self._stock_level_widget.world_list.itemDoubleClicked.connect(self._on_ok)
        self._stock_level_widget.level_list.itemDoubleClicked.connect(self._on_ok)

        self._stock_level_widget.level_list.itemClicked.connect(self._on_stock_level_selected)

        self.enemy_data_label = QLabel(parent=self, text="Enemy Data")
        self.enemy_data_spinner = Spinner(parent=self)

        self.object_data_label = QLabel(parent=self, text="Object Data")
        self.object_data_spinner = Spinner(self)

        self.object_set_label = QLabel(parent=self, text="Object Set")
        self.object_set_dropdown = QComboBox(self)
        self.object_set_dropdown.addItems(OBJECT_SET_ITEMS)

        self.button_ok = QPushButton("Ok", self)
        self.button_ok.clicked.connect(self._on_ok)
        self.button_ok.setFocus()

        self.button_cancel = QPushButton("Cancel", self)
        self.button_cancel.clicked.connect(self.close)

        # List of found levels
        self.found_levels = ROM.additional_data.found_levels.copy()
        self.found_levels.sort(key=lambda x: (x.world_number, x.level_offset))

        self.found_label = QLabel(parent=self, text="Found Levels")
        self.found_list = QListWidget(parent=self)
        for found_level in self.found_levels:
            level_descr = f"World {found_level.world_number}\t"

            level_descr += f"Level: 0x{found_level.level_offset:x}\t"
            level_descr += f"Enemy: 0x{found_level.enemy_offset:0>4x}\t"

            level_descr += OBJECT_SET_NAMES[found_level.object_set_number]

            if found_level.found_as_jump:
                level_descr += " (Jump Destination)"

            self.found_list.addItem(level_descr)

        self.found_list.itemDoubleClicked.connect(self._on_ok)
        self.found_list.itemSelectionChanged.connect(self._on_found_level_selected)

        found_level_widget = QWidget()
        found_level_layout = QGridLayout(found_level_widget)
        found_level_layout.addWidget(self.found_label, 0, 0)
        found_level_layout.addWidget(self.found_list, 1, 0)

        tab_index = 0

        self.source_selector = QTabWidget()
        self.source_selector.addTab(self._stock_level_widget, "Stock Levels")
        self.source_selector.setTabIcon(tab_index, icon("list.svg"))

        tab_index += 1

        if self.found_levels:
            self.source_selector.addTab(found_level_widget, "Found Levels")
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

        if not ROM().additional_data.managed_level_positions:
            self._stock_level_widget.world_list.setCurrentRow(0)
        else:
            first_level = ROM().additional_data.found_levels[0]
            self._fill_in_data(
                first_level.object_set_number,
                first_level.level_offset,
                first_level.enemy_offset,
            )

    def keyPressEvent(self, key_event: QKeyEvent):
        if key_event.key() == Qt.Key_Escape:
            self.reject()

    def goto_world(self, world_number: int):
        if world_number not in range(1, WORLD_COUNT + 1):
            world_number = 1

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

        self.button_ok.setFocus()

    def _on_found_level_selected(self):
        index = self.found_list.currentRow()
        self._fill_in_data(
            self.found_levels[index].object_set_number,
            self.found_levels[index].level_offset,
            self.found_levels[index].enemy_offset,
        )
        self.button_ok.setFocus()

    def _on_ok(self, _=None):
        if self._stock_level_widget.level_is_overworld:
            return

        self.object_set = self.object_set_dropdown.currentIndex()
        self.object_data_offset = self.object_data_spinner.value()
        self.enemy_data_offset = self.enemy_data_spinner.value()

        self.accept()

    def closeEvent(self, _close_event: QCloseEvent):
        self.reject()


class WorldMapLevelSelect(QScrollArea):
    level_clicked: SignalInstance = Signal(str, LevelPointerData)
    level_selected: SignalInstance = Signal(str, LevelPointerData)
    map_position_clicked: SignalInstance = Signal(Position)

    def __init__(self, world_number: int):
        super(WorldMapLevelSelect, self).__init__()

        self.ignore_levels = False
        """Set to True, if you only care about Position in the Map, not a level at the position."""

        self.world = WorldMap.from_world_number(world_number)

        level_ref = LevelRef()
        level_ref.load_level("World", self.world.layout_address, 0x0, WORLD_MAP_OBJECT_SET)

        world_settings = Settings()
        world_settings.setValue(
            "world view/show level pointers", Settings("mchlnix", "foundry").value("world view/show level pointers")
        )
        world_settings.setValue("world view/show level previews", True)
        world_settings.setValue("world view/animated tiles", True)
        world_settings.setValue("world view/show border", True)

        self.world_view = WorldView(self, level_ref, world_settings, None)

        self.world_view.setMouseTracking(True)
        self.world_view.read_only = True

        self.world_view.zoom_in()

        self.setWidget(self.world_view)

        self.setMouseTracking(True)

        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        self._try_emit(event, self.level_selected)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._try_emit(event, self.level_clicked)

    def _try_emit(self, event: QMouseEvent, level_signal: SignalInstance):
        """
        Analyzes the clicked position described in event and, if a valid level was clicked, emits the signal specified
        by level_signal.

        A map_position_clicked event will be emitted, regardless of whether a level was clicked or not.

        :param event: The mouse event describing the interaction.
        :param level_signal: The signal to emit, if a valid level was clicked.
        """
        pos = self.world_view.mapFromParent(event.position().toPoint())

        level_pos = self.world_view.to_level_point(pos)
        self.map_position_clicked.emit(level_pos)

        if self.ignore_levels:
            return

        x, y = level_pos.xy

        with suppress(ValueError):
            level_pointer = self.world.level_pointer_at(x, y)

            if level_pointer is None:
                return

            if level_pointer.data.object_set in [
                MUSHROOM_OBJECT_SET,
                SPADE_BONUS_OBJECT_SET,
            ]:
                QMessageBox.warning(
                    self,
                    "No can do",
                    "Spade and mushroom house levels are currently not supported, when getting a level address.",
                )
                event.accept()
                return

            level_signal.emit(self.world.level_name_at_position(x, y), level_pointer.data)

    def sizeHint(self) -> QSize:
        orig_size: QSize = super(WorldMapLevelSelect, self).sizeHint()
        widget_size: QSize = self.widget().sizeHint()

        size = QSize(orig_size.width(), widget_size.height())

        scrollbar_width = QScrollBar().sizeHint().width()

        return size.grownBy(QMargins(scrollbar_width, scrollbar_width, 0, 0))
