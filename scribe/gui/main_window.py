from PySide6.QtCore import QSize
from PySide6.QtGui import QAction, QActionGroup, QUndoStack, Qt
from PySide6.QtWidgets import QApplication, QFileDialog, QMenu, QMessageBox, QScrollArea

from foundry import ROM_FILE_FILTER
from foundry.game.File import ROM
from foundry.gui.MainWindow import MainWindow
from foundry.gui.WorldView import WorldView
from scribe.gui.edit_world_info import EditWorldInfo
from scribe.gui.settings import Settings
from scribe.gui.tool_window.tool_window import ToolWindow
from scribe.gui.world_view_context_menu import WorldContextMenu
from smb3parse.constants import AIRSHIP_TRAVEL_SET_COUNT
from smb3parse.levels import WORLD_COUNT
from smb3parse.levels.world_map import WorldMap as SMB3WorldMap
from smb3parse.objects.object_set import WORLD_MAP_OBJECT_SET


class ScribeMainWindow(MainWindow):
    def __init__(self, path_to_rom: str):
        super(ScribeMainWindow, self).__init__()

        self.on_open_rom(path_to_rom)

        self.world_view = WorldView(self, self.level_ref, WorldContextMenu(self.level_ref))
        self.world_view.zoom_in()
        self.world_view.zoom_in()

        self.settings = Settings("mchlnix", "smb3scribe")
        self.world_view.drawer.settings = self.settings

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.world_view)

        self.undo_stack = QUndoStack(self)
        self.undo_stack.setObjectName("undo_stack")

        self.setCentralWidget(self.scroll_area)

        self._setup_file_menu()
        self._setup_edit_menu()
        self._setup_view_menu()
        self._setup_level_menu()

        self.menuBar().addMenu(self.file_menu)
        self.menuBar().addMenu(self.edit_menu)
        self.menuBar().addMenu(self.view_menu)
        self.menuBar().addMenu(self.level_menu)

        self.tool_window = ToolWindow(self, self.level_ref)
        self.tool_window.tile_selected.connect(self.world_view.on_put_tile)
        self.tool_window.sprite_selection_changed.connect(self.world_view.select_sprite)
        self.tool_window.level_pointer_selection_changed.connect(self.world_view.select_level_pointer)

        self.show()
        self.tool_window.show()

    def _setup_file_menu(self):
        self.file_menu = QMenu("&File")
        self.file_menu.triggered.connect(self.on_file_menu)

        self.open_rom_action = self.file_menu.addAction("&Open ROM...")
        self.open_rom_action.setShortcut(Qt.CTRL + Qt.Key_O)

        self.file_menu.addSeparator()

        self.save_rom_action = self.file_menu.addAction("&Save ROM")
        self.save_rom_action.setShortcut(Qt.CTRL + Qt.Key_S)

        self.file_menu.aboutToShow.connect(lambda: self.save_rom_action.setEnabled(not self.undo_stack.isClean()))

        self.save_as_rom_action = self.file_menu.addAction("Save ROM &As...")
        self.save_as_rom_action.setShortcut(Qt.CTRL + Qt.SHIFT + Qt.Key_S)
        self.file_menu.addSeparator()
        self.quit_rom_action = self.file_menu.addAction("&Quit")

    def _setup_edit_menu(self):
        self.edit_menu = QMenu("&Edit")
        self.edit_menu.triggered.connect(self.on_edit_menu)

        self.undo_action = self.undo_stack.createUndoAction(self.edit_menu)
        self.undo_action.setShortcut(Qt.CTRL + Qt.Key_Z)

        self.redo_action = self.undo_stack.createRedoAction(self.edit_menu)
        self.redo_action.setShortcut(Qt.CTRL + Qt.SHIFT + Qt.Key_Z)

        self.edit_menu.addAction(self.undo_action)
        self.edit_menu.addAction(self.redo_action)

        self.edit_menu.addSeparator()

        self.clear_tiles_action = self.edit_menu.addAction("Clear &Tiles")
        self.clear_level_pointers_action = self.edit_menu.addAction("Clear All &Level Pointers")
        self.clear_sprites_action = self.edit_menu.addAction("Clear All &Sprites")

        self.edit_menu.addSeparator()

        self.edit_world_info = self.edit_menu.addAction("Edit World Info")

    def _setup_view_menu(self):
        self.view_menu = QMenu("&View")
        self.view_menu.triggered.connect(self.on_view_menu)

        self.grid_action = self.view_menu.addAction("&Grid")
        self.grid_action.setShortcut(Qt.CTRL + Qt.Key_G)
        self.grid_action.setCheckable(True)
        self.grid_action.setChecked(self.settings.value("world view/show grid"))

        self.view_menu.addSeparator()

        self.level_pointer_action = self.view_menu.addAction("&Level Pointers")
        self.level_pointer_action.setCheckable(True)
        self.level_pointer_action.setChecked(self.settings.value("world view/show level pointers"))

        self.level_preview_action = self.view_menu.addAction("&Tooltip with Level Preview")
        self.level_preview_action.setCheckable(True)
        self.level_preview_action.setChecked(self.settings.value("world view/show level previews"))

        self.sprite_action = self.view_menu.addAction("Overworld &Sprites")
        self.sprite_action.setCheckable(True)
        self.sprite_action.setChecked(self.settings.value("world view/show sprites"))

        self.starting_point_action = self.view_menu.addAction("Starting &Point")
        self.starting_point_action.setCheckable(True)
        self.starting_point_action.setChecked(self.settings.value("world view/show start position"))

        self.view_menu.addSeparator()

        self.airship_travel_actions = []
        for i in range(AIRSHIP_TRAVEL_SET_COUNT):
            self.airship_travel_actions.append(self.view_menu.addAction(f"&Airship Travel Path {i+1}"))
            self.airship_travel_actions[-1].setCheckable(True)
            self.airship_travel_actions[-1].setChecked(
                self.settings.value("world view/show airship paths") & 2**i == 2**i
            )

        self.view_menu.addSeparator()

        self.lock_bridge_action = self.view_menu.addAction("Lock and &Bridge Events")
        self.lock_bridge_action.setCheckable(True)
        self.lock_bridge_action.setChecked(self.settings.value("world view/show locks"))

        self.view_menu.addSeparator()

        self.show_all_action = self.view_menu.addAction("Show All")

    def _setup_level_menu(self):
        self.level_menu = QMenu("Change &Level")
        self.level_menu.triggered.connect(self.on_level_menu)

        level_menu_action_group = QActionGroup(self)

        for level_index in range(WORLD_COUNT):
            action = self.level_menu.addAction(f"World &{level_index + 1}")
            action.setCheckable(True)

            level_menu_action_group.addAction(action)

        self.level_menu.addSeparator()

        self.reload_world_action = self.level_menu.addAction("&Reload Current World")

        self.level_menu.actions()[0].trigger()

    def on_open_rom(self, path_to_rom="") -> bool:
        if not path_to_rom:
            # otherwise ask the user what new file to open
            path_to_rom, _ = QFileDialog.getOpenFileName(self, caption="Open ROM", filter=ROM_FILE_FILTER)

            if not path_to_rom:
                return False

        # Proceed loading the file chosen by the user
        try:
            ROM.load_from_file(path_to_rom)
        except IOError as exp:
            QMessageBox.warning(self, type(exp).__name__, f"Cannot open file '{path_to_rom}'.")
            return False

        return True

    def load_level(self, world_number: int):
        world = SMB3WorldMap.from_world_number(ROM(), world_number)

        self.level_ref.load_level("World", world.layout_address, 0x0, WORLD_MAP_OBJECT_SET)
        self.level_ref.level.dimensions_changed.connect(self._resize_for_level)

    def on_save_rom(self, is_save_as=False):
        if is_save_as:
            suggested_file = ROM.name

            if not suggested_file.endswith(".nes"):
                suggested_file += ".nes"

            pathname, _ = QFileDialog.getSaveFileName(
                self, caption="Save ROM as", dir=suggested_file, filter=ROM_FILE_FILTER
            )
            if not pathname:
                return  # the user changed their mind
        else:
            pathname = ROM.path

        self._save_current_changes_to_file(pathname, set_new_path=True)

        if not is_save_as:
            self.undo_stack.setClean()
            self.level_ref.data_changed.emit()

    def on_file_menu(self, action: QAction):
        if action is self.open_rom_action:
            self.on_open_rom()
            self.load_level(1)
        elif action is self.save_rom_action:
            self.on_save_rom(False)
        elif action is self.save_as_rom_action:
            self.on_save_rom(True)
        elif action is self.quit_rom_action:
            self.close()

        self.world_view.update()

    def on_edit_menu(self, action: QAction):
        if action in [self.undo_action, self.redo_action]:
            self.edit_menu.show()
        elif action is self.clear_tiles_action:
            self.world_view.clear_tiles()
        elif action is self.clear_sprites_action:
            self.world_view.clear_sprites()
        elif action is self.clear_level_pointers_action:
            self.world_view.clear_level_pointers()
        elif action is self.edit_world_info:
            EditWorldInfo(self, self.level_ref.level).exec()

        self.world_view.update()

    def on_view_menu(self, action: QAction):
        if action is self.grid_action:
            self.settings.setValue("world view/show grid", action.isChecked())
        elif action is self.level_pointer_action:
            self.settings.setValue("world view/show level pointers", action.isChecked())
        elif action is self.level_preview_action:
            self.settings.setValue("world view/show level previews", action.isChecked())
        elif action is self.sprite_action:
            self.settings.setValue("world view/show sprites", action.isChecked())
        elif action is self.starting_point_action:
            self.settings.setValue("world view/show start position", action.isChecked())
        elif action in self.airship_travel_actions:
            value = 0

            for index, action in enumerate(self.airship_travel_actions):
                if action.isChecked():
                    value += 2**index

            self.settings.setValue("world view/show airship paths", value)
        elif action is self.lock_bridge_action:
            self.settings.setValue("world view/show locks", action.isChecked())

        elif action is self.show_all_action:
            for view_action in self.view_menu.actions():
                if view_action.isCheckable() and not view_action.isChecked():
                    view_action.trigger()

            # close view menu, after everything has been triggered
            self.view_menu.hide()

        if action.isCheckable():
            # keep menu open, when checkbox has been clicked
            self.view_menu.show()

        self.world_view.update()

    def on_level_menu(self, action: QAction):
        # get index of world to change to
        if action is self.reload_world_action:
            index = self.level_ref.data.index
        else:
            index = self.level_menu.actions().index(action)

            if self.level_ref and index == self.level_ref.data.index:
                # if clicked on the world, that is already active, do nothing
                return

        # if the user decides against changing worlds, re-check the action of the current world
        if not self.safe_to_change():
            self.level_menu.actions()[self.level_ref.data.index].trigger()
            return

        # if the user is ok with changing, let's go!
        self.undo_stack.clear()
        self.load_level(index + 1)

        self._resize_for_level()

    def safe_to_change(self) -> bool:
        return self.undo_stack.isClean() or self.confirm_changes()

    def _resize_for_level(self):
        if not self.isMaximized():
            self.resize(self.sizeHint())

    def sizeHint(self) -> QSize:
        inner_width, inner_height = self.world_view.sizeHint().toTuple()

        height = inner_height + self.scroll_area.horizontalScrollBar().height() + 2 * self.scroll_area.frameWidth()
        height += self.menuBar().height()

        width = inner_width + 2 * self.scroll_area.frameWidth()

        size_hint = QSize(min(width, QApplication.primaryScreen().size().width()), height)

        return size_hint
