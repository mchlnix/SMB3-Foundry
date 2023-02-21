import tempfile
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QPoint, QSize
from PySide6.QtGui import QAction, QActionGroup, QKeySequence, QShortcut, QUndoStack, Qt
from PySide6.QtWidgets import QApplication, QFileDialog, QMenu, QMessageBox, QScrollArea, QToolBar

from foundry import ROM_FILE_FILTER, icon
from foundry.game.File import ROM
from foundry.game.gfx.GraphicsSet import GraphicsSet
from foundry.game.gfx import restore_all_palettes
from foundry.game.gfx.drawable.Block import get_block, get_tile
from foundry.gui.MainWindow import MainWindow
from foundry.gui.WorldView import WorldView
from foundry.gui.settings import Settings
from scribe.gui.commands import PutTile
from scribe.gui.menus.edit_menu import EditMenu
from scribe.gui.menus.help_menu import HelpMenu
from scribe.gui.menus.view_menu import ViewMenu
from scribe.gui.settings_dialog import SettingsDialog
from scribe.gui.tool_window.tool_window import ToolWindow
from scribe.gui.world_view_context_menu import WorldContextMenu
from smb3parse.constants import STARTING_WORLD_INDEX_ADDRESS
from smb3parse.data_points import Position
from smb3parse.levels import WORLD_COUNT, WORLD_MAP_BLANK_TILE_ID
from smb3parse.levels.world_map import WorldMap as SMB3WorldMap
from smb3parse.objects.object_set import WORLD_MAP_OBJECT_SET


class ScribeMainWindow(MainWindow):
    def __init__(self, path_to_rom: str):
        super(ScribeMainWindow, self).__init__()

        self.setWindowIcon(icon("scribe.ico"))

        self.level_ref.level_changed.connect(self._resize_for_level)

        self.undo_stack = QUndoStack(self)
        self.undo_stack.setObjectName("undo_stack")

        self.menu_toolbar = None

        self.settings = Settings("mchlnix", "smb3scribe")

        self.check_for_update_on_startup()

        self.on_open_rom(path_to_rom)

        self.context_menu = WorldContextMenu(self.level_ref)

        self.context_menu.cut_action.triggered.connect(self._cut_objects)
        self.context_menu.copy_action.triggered.connect(self._copy_objects)
        self.context_menu.paste_action.triggered.connect(
            lambda _: self._paste_objects(self.context_menu.get_position())
        )
        self.context_menu.paste_action.setShortcut(Qt.CTRL | Qt.Key_V)

        self.world_view = WorldView(self, self.level_ref, self.settings, self.context_menu)
        self.world_view.zoom_in()
        self.world_view.zoom_in()

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.world_view)

        self.setCentralWidget(self.scroll_area)

        self._setup_file_menu()
        self._setup_edit_menu()
        self._setup_view_menu()
        self._setup_level_menu()
        self._setup_help_menu()

        self.tool_window = ToolWindow(self, self.level_ref)
        self.tool_window.tile_selected.connect(self.world_view.on_put_tile)
        self.tool_window.sprite_selection_changed.connect(self.world_view.select_sprite)
        self.tool_window.level_pointer_selection_changed.connect(self.world_view.select_level_pointer)
        self.tool_window.locks_selection_changed.connect(self.world_view.select_locks_and_bridges)

        self.menu_toolbar = QToolBar("Menu Toolbar", self)
        self.menu_toolbar.setOrientation(Qt.Horizontal)
        self.menu_toolbar.setIconSize(QSize(20, 20))

        self.menu_toolbar.addAction(self.settings_action)
        self.menu_toolbar.addSeparator()
        self.menu_toolbar.addAction(self.open_rom_action)
        self.menu_toolbar.addAction(self.save_rom_action)

        self.menu_toolbar.addSeparator()

        self.menu_toolbar.addAction(self.edit_menu.undo_action)
        self.menu_toolbar.addAction(self.edit_menu.redo_action)

        self.menu_toolbar.addSeparator()

        play_action = self.menu_toolbar.addAction(icon("play-circle.svg"), "Play Level")
        play_action.triggered.connect(self.on_play)
        play_action.setWhatsThis("Opens an emulator with the current Level set to 1-1.\nSee Settings.")

        self.menu_toolbar.addSeparator()

        zoom_out_action = self.menu_toolbar.addAction(icon("zoom-out.svg"), "Zoom Out")
        zoom_out_action.triggered.connect(self.world_view.zoom_out)
        zoom_out_action.triggered.connect(self._resize_for_level)
        zoom_in_action = self.menu_toolbar.addAction(icon("zoom-in.svg"), "Zoom In")
        zoom_in_action.triggered.connect(self.world_view.zoom_in)
        zoom_in_action.triggered.connect(self._resize_for_level)

        self.menu_toolbar.addSeparator()

        self.menu_toolbar.addAction(self.edit_menu.edit_world_info)

        self.addToolBar(Qt.TopToolBarArea, self.menu_toolbar)

        QShortcut(QKeySequence(Qt.CTRL | Qt.Key_X), self, self._cut_objects)
        QShortcut(QKeySequence(Qt.CTRL | Qt.Key_C), self, self._copy_objects)
        QShortcut(QKeySequence(Qt.CTRL | Qt.Key_V), self, self._paste_objects)

        self._resize_for_level()

        self.show()
        self.tool_window.show()

    def _setup_file_menu(self):
        self.file_menu = QMenu("&File")
        self.file_menu.triggered.connect(self.on_file_menu)

        self.open_rom_action = self.file_menu.addAction("&Open ROM...")
        self.open_rom_action.setShortcut(Qt.CTRL | Qt.SHIFT | Qt.Key_O)
        self.open_rom_action.setIcon(icon("folder.svg"))

        self.file_menu.addSeparator()

        self.save_rom_action = self.file_menu.addAction("&Save ROM")
        self.save_rom_action.setShortcut(Qt.CTRL | Qt.Key_S)
        self.save_rom_action.setIcon(icon("save.svg"))

        self.save_rom_action.setEnabled(False)
        self.undo_stack.cleanChanged.connect(lambda: self.save_rom_action.setEnabled(not self.undo_stack.isClean()))

        self.save_as_rom_action = self.file_menu.addAction("Save ROM &As...")
        self.save_as_rom_action.setShortcut(Qt.CTRL | Qt.SHIFT | Qt.Key_S)
        self.save_as_rom_action.setIcon(icon("save.svg"))
        self.file_menu.addSeparator()

        self.settings_action = self.file_menu.addAction("Editor Settings")
        self.settings_action.setIcon(icon("sliders.svg"))
        self.settings_action.triggered.connect(self._on_show_settings)

        self.file_menu.addSeparator()

        self.quit_rom_action = self.file_menu.addAction("&Quit")
        self.quit_rom_action.setIcon(icon("power.svg"))

        self.menuBar().addMenu(self.file_menu)

    def _setup_edit_menu(self):
        self.edit_menu = EditMenu(self)
        self.edit_menu.triggered.connect(self.world_view.update)

        self.menuBar().addMenu(self.edit_menu)

    def _setup_view_menu(self):
        self.view_menu = ViewMenu(self, self.world_view)
        self.view_menu.triggered.connect(self.world_view.update)
        self.view_menu.triggered.connect(self._resize_for_level)

        self.menuBar().addMenu(self.view_menu)

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
        self.reload_world_action.setIcon(icon("refresh-cw.svg"))

        # load world 1 on startup
        self.level_menu.actions()[0].trigger()

        self.menuBar().addMenu(self.level_menu)

    def _setup_help_menu(self):
        self.help_menu = HelpMenu(self)

        self.menuBar().addMenu(self.help_menu)

    def _on_show_settings(self):
        SettingsDialog(self.settings, self).exec()

    def _cut_objects(self):
        self._copy_objects()
        self.remove_selected_objects()

        self.world_view.update()

    def remove_selected_objects(self):
        selected_objects = [obj for obj in self.world_view.world.get_selected_tiles() if obj.selected]

        if not selected_objects:
            return

        self.undo_stack.beginMacro("Remove Selected Tiles")

        for obj in selected_objects:
            self.undo_stack.push(PutTile(self.level_ref.level, obj.pos, WORLD_MAP_BLANK_TILE_ID))

        self.undo_stack.endMacro()

    def _copy_objects(self):
        selected_objects = self.world_view.get_selected_objects().copy()

        if selected_objects:
            self.context_menu.set_copied_objects(selected_objects)

        self.world_view.update()

    def _paste_objects(self, q_point: Optional[QPoint] = None):
        if not (copy_data := self.context_menu.get_copied_objects())[0]:
            return

        if q_point is not None:
            paste_target = self.world_view.to_level_point(self.world_view.mapFromGlobal(q_point))
        else:
            paste_target = self.world_view.last_mouse_position

        copied_objects, copy_origin = copy_data

        diff = paste_target - copy_origin

        self.undo_stack.beginMacro(f"Pasting {len(copied_objects)} Objects")

        for obj in copied_objects:
            target_pos = Position.from_xy(*obj.get_position()) + diff

            if not self.world_view.world.point_in(*target_pos.xy):
                continue

            self.undo_stack.push(PutTile(self.level_ref.level, target_pos, obj.type))

        self.undo_stack.endMacro()

        self.world_view.update()

    def on_play(self, temp_dir=Path()):
        """
        Copies the ROM, including the current level, to a temporary directory, saves the current level as level 1-1 and
        opens the rom in an emulator.
        """
        temp_dir = Path(tempfile.gettempdir()) / "smb3scribe"
        temp_dir.mkdir(parents=True, exist_ok=True)

        super(ScribeMainWindow, self).on_play(temp_dir)

    def _save_changes_to_instaplay_rom(self, path_to_temp_rom) -> bool:
        temp_rom = ROM.from_file(path_to_temp_rom)
        self.world_view.world.save_to_rom(temp_rom)

        temp_rom.write(STARTING_WORLD_INDEX_ADDRESS, self.world_view.world.internal_world_map.number - 1)

        temp_rom.save_to(path_to_temp_rom)

        return True

    def on_open_rom(self, path_to_rom=""):
        if not self.safe_to_change():
            return

        if not path_to_rom:
            # otherwise ask the user what new file to open
            path_to_rom, _ = QFileDialog.getOpenFileName(
                self, caption="Open ROM", dir=self.settings.value("editor/default dir path"), filter=ROM_FILE_FILTER
            )

            if not path_to_rom:
                if not ROM.is_loaded():
                    quit()
                else:
                    return

        # Proceed loading the file chosen by the user
        try:
            ROM.load_from_file(path_to_rom)
            get_block.cache_clear()
            get_tile.cache_clear()
            GraphicsSet.from_number.cache_clear()
            restore_all_palettes()
        except IOError as exp:
            QMessageBox.warning(self, type(exp).__name__, f"Cannot open file '{path_to_rom}'.")
            return

    def load_level(self, world_number: int):
        world = SMB3WorldMap.from_world_number(ROM(), world_number)

        self.level_ref.load_level(f"World {world_number}", world.layout_address, 0x0, WORLD_MAP_OBJECT_SET)
        self.level_ref.level.dimensions_changed.connect(self._resize_for_level)

        self.setWindowTitle(f"{self.level_ref.level.name} - SMB3 Scribe")

        self.undo_stack.clear()

    def on_save_rom(self, is_save_as=False):
        if is_save_as:
            suggested_file = ROM.name

            if not suggested_file.endswith(".nes"):
                suggested_file += ".nes"

            pathname, _ = QFileDialog.getSaveFileName(
                self,
                caption="Save ROM as",
                dir=f"{self.settings.value('editor/default dir path')}/{suggested_file}",
                filter=ROM_FILE_FILTER,
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

        if self.menu_toolbar:
            height += self.menu_toolbar.height()

        width = inner_width + 2 * self.scroll_area.frameWidth()

        size_hint = QSize(min(width, QApplication.primaryScreen().size().width()), height)

        return size_hint
