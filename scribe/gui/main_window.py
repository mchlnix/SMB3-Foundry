import tempfile
from pathlib import Path
from typing import cast

from PySide6.QtCore import QPoint, QSize
from PySide6.QtGui import QAction, QActionGroup, QKeySequence, QShortcut, Qt, QUndoStack
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QMenu,
    QMessageBox,
    QScrollArea,
    QToolBar,
)

from foundry import ASM_FILE_FILTER, ROM_FILE_FILTER, icon
from foundry.game.File import ROM
from foundry.game.level.WorldMap import WorldMap
from foundry.gui.MainWindow import MainWindow
from foundry.gui.settings import Settings
from foundry.gui.visualization.world.WorldView import WorldView
from scribe.gui.commands import PutTile
from scribe.gui.menus.edit_menu import EditMenu
from scribe.gui.menus.help_menu import HelpMenu
from scribe.gui.menus.view_menu import ViewMenu
from scribe.gui.settings_dialog import SettingsDialog
from scribe.gui.tool_window.tool_window import ToolWindow
from scribe.gui.world_view_context_menu import WorldContextMenu
from smb3parse.constants import MAPOBJ_ASM_SYMBOLS, STARTING_WORLD_INDEX_ADDRESS
from smb3parse.data_points import Position
from smb3parse.levels import (
    MAX_SCREEN_COUNT,
    WORLD_COUNT,
    WORLD_MAP_BLANK_TILE_ID,
    WORLD_MAP_HEIGHT,
    WORLD_MAP_SCREEN_WIDTH,
)
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
        self.context_menu.paste_action.setShortcut(Qt.Modifier.CTRL | Qt.Key.Key_V)

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

        QShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_X), self, self._cut_objects)
        QShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_C), self, self._copy_objects)
        QShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_V), self, self._paste_objects)

        self._resize_for_level()

        self.show()
        self.tool_window.show()

    def _setup_file_menu(self):
        self.file_menu = QMenu("&File")
        self.file_menu.triggered.connect(self.on_file_menu)

        self.open_rom_action = self.file_menu.addAction("&Open ROM...")
        self.open_rom_action.setShortcut(Qt.Modifier.CTRL | Qt.Modifier.SHIFT | Qt.Key.Key_O)
        self.open_rom_action.setIcon(icon("folder.svg"))

        self.file_menu.addSeparator()

        self.save_rom_action = self.file_menu.addAction("&Save ROM")
        self.save_rom_action.setShortcut(Qt.Modifier.CTRL | Qt.Key.Key_S)
        self.save_rom_action.setIcon(icon("save.svg"))

        self.save_rom_action.setEnabled(False)
        self.undo_stack.cleanChanged.connect(lambda: self.save_rom_action.setEnabled(not self.undo_stack.isClean()))

        self.save_as_rom_action = self.file_menu.addAction("Save ROM &As...")
        self.save_as_rom_action.setShortcut(Qt.Modifier.CTRL | Qt.Modifier.SHIFT | Qt.Key.Key_S)
        self.save_as_rom_action.setIcon(icon("save.svg"))

        self.file_menu.addSeparator()

        self.export_map_action = self.file_menu.addAction("Export Map ASM files...")
        self.export_map_action.setIcon(icon("save.svg"))

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

        self.edit_menu.world_order_maybe_changed.connect(self._on_world_order_changed)

        self.menuBar().addMenu(self.edit_menu)

    def _setup_view_menu(self):
        self.view_menu = ViewMenu(self, self.world_view)
        self.view_menu.triggered.connect(self.world_view.update)
        self.view_menu.triggered.connect(self._resize_for_level)

        self.menuBar().addMenu(self.view_menu)

    def _setup_level_menu(self):
        self.world_menu = QMenu("Change &World")
        self.world_menu.triggered.connect(self.on_level_menu)

        level_menu_action_group = QActionGroup(self)

        for level_index in range(WORLD_COUNT):
            action = self.world_menu.addAction(f"World &{level_index + 1}")
            action.setCheckable(True)

            level_menu_action_group.addAction(action)

        self.world_menu.addSeparator()

        self.reload_world_action = self.world_menu.addAction("&Reload Current World")
        self.reload_world_action.setIcon(icon("refresh-cw.svg"))

        # load world 1 on startup
        self.world_menu.actions()[0].trigger()

        self.menuBar().addMenu(self.world_menu)

    def _setup_help_menu(self):
        self.help_menu = HelpMenu(self)

        self.menuBar().addMenu(self.help_menu)

    def _on_world_order_changed(self):
        """If the world order was changed through the world info dialog, change the selected world in the world menu."""
        new_world_index = self.level_ref.level.internal_world_map.data.index

        self.world_menu.actions()[new_world_index].setChecked(True)

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
            self.undo_stack.push(PutTile(self.level_ref, obj.pos, WORLD_MAP_BLANK_TILE_ID))

        self.undo_stack.endMacro()

    def _copy_objects(self):
        selected_objects = self.world_view.get_selected_objects().copy()

        if selected_objects:
            self.context_menu.set_copied_objects(selected_objects)

        self.world_view.update()

    def _paste_objects(self, q_point: QPoint | None = None):
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

            self.undo_stack.push(PutTile(self.level_ref, target_pos, obj.type))

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

        temp_rom.write(
            STARTING_WORLD_INDEX_ADDRESS,
            self.world_view.world.internal_world_map.number - 1,
        )

        temp_rom.save_to(path_to_temp_rom)

        return True

    def on_open_rom(self, path_to_rom=""):
        if not self.safe_to_change():
            return

        if not path_to_rom:
            # otherwise ask the user what new file to open
            path_to_rom, _ = QFileDialog.getOpenFileName(
                self,
                caption="Open ROM",
                dir=self.settings.value("editor/default_dir_path"),
                filter=ROM_FILE_FILTER,
            )

            if not path_to_rom:
                if not ROM.is_loaded():
                    quit()
                else:
                    return

        # Proceed loading the file chosen by the user
        try:
            ROM.load_from_file(path_to_rom)
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
                dir=f"{self.settings.value('editor/default_dir_path')}/{suggested_file}",
                filter=ROM_FILE_FILTER,
            )
            if not pathname:
                return  # the user changed their mind
        else:
            pathname = ROM.path

        saved_successfully = self._save_current_changes_to_file(pathname, set_new_path=True)

        if saved_successfully and not is_save_as:
            self.undo_stack.setClean()
            self.level_ref.data_changed.emit()

    def on_export_map(self):
        level = cast(WorldMap, self.level_ref.level)

        if True:
            # get file basename
            pathname, _ = QFileDialog.getSaveFileName(
                self,
                caption="Export Map as ASM",
                dir=self.settings.value("editor/default_dir_path"),
                filter=ASM_FILE_FILTER,
            )

            if not pathname:
                return

            path = Path(pathname)

            base_name = self._harmonize_base_name(path)

        # L - Tile indexes that visually make up the World Map
        layout_text = self._make_layout_asm(level)

        # O - The ID of each Sprite on the World Map (Speech Bubbles, Hammer Bros, etc.), 9 for each map
        object_text = "\t.byte "
        object_text += ", ".join([MAPOBJ_ASM_SYMBOLS[obj.type] for obj in level.sprites])

        # OH - The higher 4 bits of the x position of each Sprite. The screen number, since a screen is 16 columns wide.
        screen_text = "\t.byte "
        screen_text += ", ".join([f"${obj.data.screen:02X}" for obj in level.sprites])

        # OX - THe lower 4 bits of the x position of each Sprite. It's the column number inside the screen.
        x_pos_text = "\t.byte "
        x_pos_text += ", ".join([f"${obj.data.pos.x<<4:02X}" for obj in level.sprites])

        # OY - The y position of each Sprite. It's the row number inside the screen.
        # for some reason shifted into the high nibble
        y_pos_text = "\t.byte "
        y_pos_text += ", ".join([f"${obj.data.pos.y<<4:02X}" for obj in level.sprites])

        # OI - The index of the item the Sprite gives. No ASM labels available, so write the raw values.
        item_text = "\t.byte "
        item_text += ", ".join([f"${obj.data.item:02X}" for obj in level.sprites])

        # S - Structure Block, containing a lot of offsets into miscellaneous world map information.
        structure_text = self._make_structure_asm(level)

        (path.parent / f"{base_name}L.asm").write_text(layout_text)
        (path.parent / f"{base_name}O.asm").write_text(object_text.removesuffix(", "))
        (path.parent / f"{base_name}OH.asm").write_text(screen_text.removesuffix(", "))
        (path.parent / f"{base_name}OX.asm").write_text(x_pos_text.removesuffix(", "))
        (path.parent / f"{base_name}OY.asm").write_text(y_pos_text.removesuffix(", "))
        (path.parent / f"{base_name}OI.asm").write_text(item_text.removesuffix(", "))
        (path.parent / f"{base_name}S.asm").write_text(structure_text.removesuffix(", "))

    @staticmethod
    def _make_structure_asm(level: WorldMap) -> str:
        world_num = level.data.index + 1

        template = (
            "W1_InitIndex:\t.byte $00, (W1_ByRowType_S2 - W1_ByRowType), (W1_ByRowType_S3 - W1_ByRowType), "
            "(W1_ByRowType_S4 - W1_ByRowType)\n"
        )

        # first line, outlining certain offsets
        structure_text = template.replace("W1", f"W{world_num}")

        # bytes outlining the y position and object set of each level, one line per screen
        row_type_text = ""

        # bytes outlining the screen and x position within the screen of each level, one line per screen
        screen_column_text = ""

        # words (2 bytes) being the offset of the enemy/item data of each level, one line per screen
        enemy_item_offset_text = ""

        # words (2 bytes) being the offset of the level object data of each level, one line per screen
        level_layout_offset_text = ""

        for screen_no in range(MAX_SCREEN_COUNT):
            if screen_no == 0:
                # the line for the first screen has no suffix
                screen_no_suffix = ""
            else:
                screen_no_suffix = f"_S{screen_no + 1}"

            row_type_text += f"W{world_num}_ByRowType{screen_no_suffix}:\t.byte "
            screen_column_text += f"W{world_num}_ByScrCol{screen_no_suffix}:\t.byte "
            enemy_item_offset_text += f"W{world_num}_ObjSets{screen_no_suffix}:\t.word "
            level_layout_offset_text += f"W{world_num}_LevelLayout{screen_no_suffix}:\t.word "

            for level_pointer in level.level_pointers:
                if level_pointer.data.screen == screen_no:
                    row_and_object_set = (level_pointer.data.y << 4) + level_pointer.data.object_set
                    screen_and_column = (level_pointer.data.screen << 4) + level_pointer.data.x

                    row_type_text += f"${row_and_object_set:02X}, "
                    screen_column_text += f"${screen_and_column:02X}, "

                    # TODO In the original ASM these are (mostly) labels to values, find a way to match them?
                    enemy_item_offset_text += f"${level_pointer.data.enemy_offset:04X}, "
                    level_layout_offset_text += f"${level_pointer.data.level_offset:04X}, "

            for suffix in (", ", "\t.byte ", "\t.word "):
                row_type_text = row_type_text.removesuffix(suffix)
                screen_column_text = screen_column_text.removesuffix(suffix)
                enemy_item_offset_text = enemy_item_offset_text.removesuffix(suffix)
                level_layout_offset_text = level_layout_offset_text.removesuffix(suffix)

            row_type_text += "\n"
            screen_column_text += "\n"
            enemy_item_offset_text += "\n"
            level_layout_offset_text += "\n"

        structure_text += "".join((row_type_text, screen_column_text, enemy_item_offset_text, level_layout_offset_text))

        return structure_text

    @staticmethod
    def _make_layout_asm(level: WorldMap) -> str:
        layout_text = ""

        for index, tile in enumerate(level.objects):

            if index > 0 and index % (WORLD_MAP_HEIGHT * WORLD_MAP_SCREEN_WIDTH) == 0:
                layout_text = layout_text.removesuffix(", ")

                layout_text += "\n"

            if index % WORLD_MAP_SCREEN_WIDTH == 0:
                layout_text = layout_text.removesuffix(", ")

                layout_text += "\n\t.byte "

            layout_text += f"${tile.type:02X}, "

        layout_text = layout_text.removesuffix(", ")
        layout_text = layout_text.rstrip() + "\n\n" + "\t.byte $FF"

        return layout_text

    def _harmonize_base_name(self, path: Path):
        potential_base_name = self._base_name_from_world_asm(path)

        if (path.parent / f"{potential_base_name}L.asm").is_file():
            should_change_base_name = (
                QMessageBox.question(
                    self,
                    "Export Map as ASM",
                    "It seems like you clicked on an ASM file of an existing World Map.\n\n"
                    f"Should we overwrite {potential_base_name}L.asm etc, instead of saving under "
                    f"{path.stem}L.asm, {path.stem}O.asm etc?",
                )
                == QMessageBox.StandardButton.Yes
            )

            if should_change_base_name:
                return potential_base_name

        return path.stem

    @staticmethod
    def _base_name_from_world_asm(path: Path):
        """
        A world map is split across 7 different asm files, so if the user selects one of those, get the actual World
        name instead.
        """
        asm_name_suffixes = ["OH", "OI", "OX", "OY", "L", "O", "S"]

        base_name = path.stem

        if path.is_file():
            for asm_suffix in asm_name_suffixes:
                if not base_name.endswith(asm_suffix):
                    continue

                real_base_name = base_name.removesuffix(asm_suffix)

                for other_suffixes in asm_name_suffixes:
                    if asm_suffix == other_suffixes:
                        continue

                    if not Path(path.parent / f"{real_base_name}{other_suffixes}.asm").is_file():
                        break
                else:
                    base_name = real_base_name
                    break

        return base_name

    def on_file_menu(self, action: QAction):
        if action is self.open_rom_action:
            self.on_open_rom()
            self.load_level(1)
        elif action is self.save_rom_action:
            self.on_save_rom(False)
        elif action is self.save_as_rom_action:
            self.on_save_rom(True)
        elif action is self.export_map_action:
            self.on_export_map()
        elif action is self.quit_rom_action:
            self.close()

        self.world_view.update()

    def on_level_menu(self, action: QAction):
        # get index of world to change to
        if action is self.reload_world_action:
            index = self.level_ref.data.index
        else:
            index = self.world_menu.actions().index(action)

            if self.level_ref and index == self.level_ref.data.index:
                # if clicked on the world, that is already active, do nothing
                return

        # if the user decides against changing worlds, re-check the action of the current world
        if not self.safe_to_change():
            self.world_menu.actions()[self.level_ref.data.index].trigger()
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
