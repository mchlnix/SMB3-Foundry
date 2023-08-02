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
from foundry.game.level.Level import Level
from foundry.game.level.LevelRef import LevelRef
from foundry.game.level.WorldMap import WorldMap
from foundry.gui import OBJECT_SET_ITEMS, WORLD_ITEMS
from foundry.gui.WorldView import WorldView
from foundry.gui.settings import Settings
from foundry.gui.widgets.Spinner import Spinner
from smb3parse.data_points import LevelPointerData, Position
from smb3parse.levels import HEADER_LENGTH, WORLD_COUNT
from smb3parse.objects.object_set import (
    MUSHROOM_OBJECT_SET,
    SPADE_BONUS_OBJECT_SET,
    WORLD_MAP_OBJECT_SET,
)

WORLD_1_INDEX = 0
LOST_LEVELS_INDEX = 8
OVERWORLD_MAPS_INDEX = 9


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

        self.world_label = QLabel(parent=self, text="World")
        self.world_list = QListWidget(parent=self)
        self.world_list.addItems(WORLD_ITEMS)

        self.world_list.itemDoubleClicked.connect(self.on_ok)
        self.world_list.itemSelectionChanged.connect(self.on_world_click)

        self.level_label = QLabel(parent=self, text="Level")
        self.level_list = QListWidget(parent=self)

        self.level_list.itemDoubleClicked.connect(self.on_ok)
        self.level_list.itemSelectionChanged.connect(self.on_level_click)




        self.enemy_data_label = QLabel(parent=self, text="Enemy Data")
        self.enemy_data_spinner = Spinner(parent=self)

        self.object_data_label = QLabel(parent=self, text="Object Data")
        self.object_data_spinner = Spinner(self)

        self.object_set_label = QLabel(parent=self, text="Object Set")
        self.object_set_dropdown = QComboBox(self)
        self.object_set_dropdown.addItems(OBJECT_SET_ITEMS)

        self.button_ok = QPushButton("Ok", self)
        self.button_ok.clicked.connect(self.on_ok)
        self.button_ok.setFocus()

        self.button_cancel = QPushButton("Cancel", self)
        self.button_cancel.clicked.connect(self.close)

        stock_level_widget = QWidget()
        stock_level_layout = QGridLayout(stock_level_widget)

        stock_level_layout.addWidget(self.world_label, 0, 0)
        stock_level_layout.addWidget(self.level_label, 0, 1)

        stock_level_layout.addWidget(self.world_list, 1, 0)
        stock_level_layout.addWidget(self.level_list, 1, 1)


        # List of found levels
        self.found_levels = [ ]
        for found_level in ROM.additional_data.found_levels:
            self.found_levels.append(found_level)
        self.found_levels.sort(key=lambda x: (x.object_set_number, x.level_offset))
        
        self.found_label = QLabel(parent=self, text="Found Levels")
        self.found_list = QListWidget(parent=self)
        for found_level in self.found_levels:
            level_descr = OBJECT_SET_ITEMS[found_level.object_set_number]
            level_descr += ", Level Offset: 0x%0.4x" % found_level.level_offset
            level_descr +=  ", Enemy Offset: 0x%0.4x" % found_level.enemy_offset
            if found_level.found_in_world:
                level_descr += ", (World " + str(found_level.world_number) + ")"
            elif found_level.found_as_jump:
                level_descr += ", (Jump Destination)"            
            self.found_list.addItem(level_descr)

        self.found_list.itemDoubleClicked.connect(self.on_ok)
        self.found_list.itemSelectionChanged.connect(self.on_found_click)

        found_level_widget = QWidget()
        found_level_layout = QGridLayout(found_level_widget)
        found_level_layout.addWidget(self.found_label, 0, 0)
        found_level_layout.addWidget(self.found_list, 1, 0)



        self.source_selector = QTabWidget()
        self.source_selector.addTab(stock_level_widget, "Stock Levels")
        self.source_selector.setTabIcon(0, icon("list.svg"))

        self.source_selector.addTab(found_level_widget, "Found Levels")
        self.source_selector.setTabIcon(1, icon("list.svg"))



        for world_number in range(1, WORLD_COUNT):
            world_map_select = WorldMapLevelSelect(world_number)
            world_map_select.level_clicked.connect(self._on_level_selected_via_world_map)
            world_map_select.level_selected.connect(self._on_level_selected_via_world_map)
            world_map_select.level_selected.connect(self.on_ok)

            self.source_selector.addTab(world_map_select, f"World {world_number}")
            self.source_selector.setTabIcon(world_number + 1, icon("globe.svg"))

        # show world 1 by default
        if self.source_selector.count() > 1:
            self.source_selector.setCurrentIndex(1)

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

        self.world_list.setCurrentRow(WORLD_1_INDEX)  # select Level 1-1

        if not ROM().additional_data.managed_level_positions:
            self.on_world_click()
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

    def on_world_click(self):
        index = self.world_list.currentRow()

        assert index >= 0

        if index == OVERWORLD_MAPS_INDEX:
            world_number = 0  # world maps
        else:
            world_number = index + 1

        self.level_list.clear()

        # skip first meaningless item
        for level in Level.offsets[1:]:
            if level.game_world == world_number:
                if level.name:
                    self.level_list.addItem(level.name)

        if self.level_list.count():
            self.level_list.setCurrentRow(0)

            self.on_level_click()

    def on_level_click(self):
        index = self.level_list.currentRow()

        assert index >= 0

        level_is_lost = self.world_list.currentRow() == LOST_LEVELS_INDEX
        level_is_overworld = self.world_list.currentRow() == OVERWORLD_MAPS_INDEX

        self.world_index = self.world_list.currentRow() + 1

        if level_is_overworld:
            level_array_offset = index + 1
            self.level_name = ""
        else:
            level_array_offset = Level.world_indexes[self.world_index] + index + 1

            if level_is_lost:
                self.level_name = "Lost World, "
            else:
                self.level_name = f"World {self.world_index}, "

        if level_is_lost:
            # selected a "lost level" that isn't actually in world 9
            self.world_index = 1

        self.level_name += f"{Level.offsets[level_array_offset].name}"

        object_data_for_lvl = Level.offsets[level_array_offset].rom_level_offset

        if not level_is_overworld:
            object_data_for_lvl -= HEADER_LENGTH

        if not level_is_overworld:
            enemy_data_for_lvl = Level.offsets[level_array_offset].enemy_offset
        else:
            enemy_data_for_lvl = 0

        if enemy_data_for_lvl > 0:
            # data in look up table is off by one, since workshop ignores the first byte
            enemy_data_for_lvl -= 1

        self.enemy_data_spinner.setEnabled(not level_is_overworld)

        object_set_index = Level.offsets[level_array_offset].real_obj_set
        self.button_ok.setDisabled(level_is_overworld)

        self._fill_in_data(object_set_index, object_data_for_lvl, enemy_data_for_lvl)

    def _fill_in_data(self, object_set: int, layout_address: int, enemy_address: int):
        self.object_set_dropdown.setCurrentIndex(object_set)
        self.object_data_spinner.setValue(layout_address)
        self.enemy_data_spinner.setValue(enemy_address)

    def _on_level_selected_via_world_map(self, level_name: str, level_pointer: LevelPointerData):
        self.level_name = level_name

        if self.clicked_level_pointer == level_pointer:
            # same level was clicked again,
            self.on_ok()
        else:
            self.clicked_level_pointer = level_pointer

        self.world_index = level_pointer.world.index + 1

        self._fill_in_data(
            level_pointer.object_set,
            level_pointer.level_address,
            level_pointer.enemy_address,
        )

        self.button_ok.setFocus()


    def on_found_click(self):
        index = self.found_list.currentRow()
        self._fill_in_data(
            self.found_levels[index].object_set_number,
            self.found_levels[index].level_offset,
            self.found_levels[index].enemy_offset,
        )
        self.button_ok.setFocus()


    def on_ok(self, _=None):
        if self.world_list.currentRow() == OVERWORLD_MAPS_INDEX:
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
