from PySide6.QtGui import QAction
from PySide6.QtWidgets import QFileDialog, QMainWindow, QMenu, QMessageBox

from foundry.game.File import ROM
from foundry.game.level.LevelRef import LevelRef
from foundry.gui.MainWindow import ROM_FILE_FILTER
from foundry.gui.WorldView import WorldView
from scribe.gui.tool_window.tool_window import ToolWindow
from scribe.gui.world_view_context_menu import WorldContextMenu
from smb3parse.levels.world_map import WorldMap
from smb3parse.objects.object_set import WORLD_MAP_OBJECT_SET


class MainWindow(QMainWindow):
    def __init__(self, path_to_rom: str):
        super(MainWindow, self).__init__()

        self.on_open_rom(path_to_rom)

        self.world = WorldMap.from_world_number(ROM(), 1)

        self.level_ref = LevelRef()
        self.level_ref.load_level("World", self.world.layout_address, 0x0, WORLD_MAP_OBJECT_SET)

        self.world_view = WorldView(self, self.level_ref, WorldContextMenu(self.level_ref))
        self.world_view.zoom_in()
        self.world_view.zoom_in()

        self._setup_file_menu()
        self._setup_edit_menu()
        self._setup_view_menu()

        self.menuBar().addMenu(self.file_menu)
        self.menuBar().addMenu(self.edit_menu)
        self.menuBar().addMenu(self.view_menu)

        self.setCentralWidget(self.world_view)

        self.tool_window = ToolWindow(self)

        self.show()
        self.tool_window.show()

    def _setup_file_menu(self):
        self.file_menu = QMenu("File")
        self.file_menu.triggered.connect(self.on_file_menu)

        self.open_rom_action = self.file_menu.addAction("Open ROM...")
        self.save_rom_action = self.file_menu.addAction("Save ROM")
        self.save_as_rom_action = self.file_menu.addAction("Save ROM As...")
        self.file_menu.addSeparator()
        self.quit_rom_action = self.file_menu.addAction("Quit")

    def _setup_edit_menu(self):
        self.edit_menu = QMenu("Edit")
        self.edit_menu.triggered.connect(self.on_edit_menu)

        self.delete_tiles_action = self.edit_menu.addAction("Delete All Tiles")
        self.delete_level_pointers_action = self.edit_menu.addAction("Delete All Level Pointers")
        self.delete_sprites_action = self.edit_menu.addAction("Delete All Sprites")

    def _setup_view_menu(self):
        self.view_menu = QMenu("View")
        self.view_menu.triggered.connect(self.on_view_menu)

        self.level_pointer_action = self.view_menu.addAction("Show Level Pointers")
        self.level_pointer_action.setCheckable(True)
        self.level_pointer_action.setChecked(self.world_view.draw_level_pointers)

        self.sprite_action = self.view_menu.addAction("Show Overworld Sprites")
        self.sprite_action.setCheckable(True)
        self.sprite_action.setChecked(self.world_view.draw_sprites)

        self.starting_point_action = self.view_menu.addAction("Show Starting Point")
        self.starting_point_action.setCheckable(True)
        self.starting_point_action.setChecked(self.world_view.draw_start)

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
            self.level_ref.level.changed = False
            self.level_ref.data_changed.emit()

    def _save_current_changes_to_file(self, pathname: str, set_new_path):
        raise NotImplementedError

        for offset, data in self.level_ref.to_bytes():
            ROM().bulk_write(data, offset)

        try:
            ROM().save_to_file(pathname, set_new_path)
        except IOError as exp:
            QMessageBox.warning(self, f"{type(exp).__name__}", f"Cannot save ROM data to file '{pathname}'.")

    def on_file_menu(self, action: QAction):
        if action is self.open_rom_action:
            self.on_open_rom()
        elif action is self.save_rom_action:
            self.save_rom_action()
        elif action is self.save_as_rom_action:
            self.on_save_rom(True)
        elif action is self.quit_rom_action:
            self.close()

        self.world_view.update()

    def on_edit_menu(self, action: QAction):
        if action is self.delete_tiles_action:
            self.level_ref.level.remove_all_tiles()

        self.world_view.update()

    def on_view_menu(self, action: QAction):
        if action is self.level_pointer_action:
            self.world_view.draw_level_pointers = action.isChecked()
        elif action is self.sprite_action:
            self.world_view.draw_sprites = action.isChecked()
        elif action is self.starting_point_action:
            self.world_view.draw_start = action.isChecked()

        self.world_view.update()
