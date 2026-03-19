import base64
import json
import logging
import tempfile
from pathlib import Path
from typing import cast

from PySide6.QtCore import QPoint, QSize
from PySide6.QtGui import (
    QAction,
    QCloseEvent,
    QKeySequence,
    QMouseEvent,
    QShortcut,
    Qt,
    QUndoStack,
)
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QMenu,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from foundry import (
    NO_PARENT,
    ROM_FILE_FILTER,
    auto_save_level_data_path,
    auto_save_m3l_path,
    auto_save_rom_path,
    get_current_version_name,
    icon,
    is_nightly_version,
    is_pyinstalled,
    make_macro,
)
from foundry.features.instaplay import CantFindFirstTile, InstaPlayer, LevelNotAttached
from foundry.features.rom_reload import RomHotSwapMixin, RomWatcherMixin
from foundry.game.additional_data import LevelOrganizer
from foundry.game.File import ROM
from foundry.game.gfx import restore_all_palettes
from foundry.game.gfx.objects.in_level.enemy_item import EnemyItem
from foundry.game.gfx.objects.in_level.in_level_object import InLevelObject
from foundry.game.gfx.objects.in_level.jump import Jump
from foundry.game.gfx.objects.in_level.level_object import LevelObject
from foundry.game.gfx.Palette import PaletteGroup, save_all_palette_groups
from foundry.game.level import EnemyItemAddress, LevelAddress
from foundry.game.level.Level import Level, world_and_level_for_level_address
from foundry.game.level.WorldMap import WorldMap
from foundry.gui.asm import asm_paths_from_rom_path, load_asm_filename
from foundry.gui.commands import (
    AddEnemyAt,
    AddJump,
    AddLevelObjectAt,
    AttachLevelToRom,
    ImportASMEnemies,
    PasteObjectsAt,
    RemoveJump,
    RemoveObjects,
    ReplaceEnemy,
    ReplaceLevelObject,
    ToBackground,
    ToForeground,
)
from foundry.gui.ContextMenu import LevelContextMenu
from foundry.gui.dialogs.HeaderEditor import HeaderEditor
from foundry.gui.dialogs.JumpEditor import JumpEditor
from foundry.gui.dialogs.level_selector.LevelSelector import LevelSelector
from foundry.gui.dialogs.LevelParseProgressDialog import LevelParseProgressDialog
from foundry.gui.dialogs.ObjectSetSelector import ObjectSetSelector
from foundry.gui.dialogs.PaletteViewer import SidePalette
from foundry.gui.dialogs.SettingsDialog import POWERUPS, SettingsDialog
from foundry.gui.JumpList import JumpList
from foundry.gui.level_settings.level_settings_dialog import LevelSettingsDialog
from foundry.gui.m3l import load_m3l, load_m3l_filename, save_m3l
from foundry.gui.MainWindow import MainWindow
from foundry.gui.menus.debug_menu import DebugMenu
from foundry.gui.menus.file_menu import FileMenu
from foundry.gui.menus.help_menu import HelpMenu
from foundry.gui.menus.rom_menu import RomMenu
from foundry.gui.menus.view_menu import ViewMenu
from foundry.gui.ObjectDropdown import ObjectDropdown
from foundry.gui.ObjectList import ObjectList
from foundry.gui.ObjectStatusBar import ObjectStatusBar
from foundry.gui.settings import ASMLoadingBehavior, Settings
from foundry.gui.SpinnerPanel import SpinnerPanel
from foundry.gui.visualization.level.LevelView import LevelView
from foundry.gui.WarningList import WarningList
from foundry.gui.widgets.object_toolbar.ObjectToolBar import ObjectToolBar
from foundry.gui.widgets.size_bar.EnemySizeBar import EnemySizeBar
from foundry.gui.widgets.size_bar.LevelSizeBar import LevelSizeBar
from smb3parse.constants import Constants
from smb3parse.data_points import Position
from smb3parse.levels import HEADER_LENGTH
from smb3parse.objects.object_set import OBJECT_SET_NAMES

TOOLBAR_ICON_SIZE = QSize(20, 20)


class FoundryMainWindow(RomWatcherMixin, RomHotSwapMixin, MainWindow):
    def __init__(self):
        super(FoundryMainWindow, self).__init__()

        self.settings = Settings("mchlnix", "foundry")

        self.level_ref.level_changed.connect(self.update_gui_for_level)
        self.level_ref.palette_changed.connect(self._update_block_graphics_in_ui)

        self.setWindowIcon(icon("foundry.ico"))
        self.setStyleSheet(self.settings.value("editor/gui_style"))

        self.undo_stack = QUndoStack(self)
        self.undo_stack.setObjectName("undo_stack")

        self._protect_undo_stack = False
        """
        Sometimes we protect the undo stack from being cleared by the usual GUI logic, to be able to reapply the
        commands.
        """

        self.file_menu = FileMenu(self.level_ref, self.settings)

        self.file_menu.open_rom_action.triggered.connect(lambda _: self.on_open_rom())
        self.file_menu.open_m3l_action.triggered.connect(self.on_open_m3l)
        self.file_menu.save_rom_action.triggered.connect(self.on_save_rom)
        self.file_menu.save_rom_as_action.triggered.connect(self.on_save_rom_as)
        self.file_menu.reload_rom_action.triggered.connect(self._on_want_to_reload_rom)
        self.file_menu.import_enemy_asm_action.triggered.connect(self.on_import_enemies_from_asm)
        self.file_menu.settings_action.triggered.connect(self._on_show_settings)
        self.file_menu.exit_action.triggered.connect(lambda _: self.close())

        self.menuBar().addMenu(self.file_menu)

        self.level_menu = QMenu("&Level")

        self.undo_action = self.undo_stack.createUndoAction(self)
        self.undo_action.setIcon(icon("rotate-ccw.svg"))
        self.level_menu.addAction(self.undo_action)

        self.redo_action = self.undo_stack.createRedoAction(self)
        self.redo_action.setIcon(icon("rotate-cw.svg"))
        self.level_menu.addAction(self.redo_action)

        self.level_menu.addSeparator()

        self.new_level_action = self.level_menu.addAction("New Empty Level")
        self.new_level_action.setIcon(icon("file.svg"))
        self.new_level_action.triggered.connect(self.on_new_level)

        self.select_level_action = self.level_menu.addAction("Select New Level")
        self.select_level_action.setIcon(icon("globe.svg"))
        self.select_level_action.triggered.connect(self.open_level_selector)

        self.level_menu.addSeparator()

        test_level_action = self.level_menu.addAction(icon("play-circle.svg"), "Test Level")
        test_level_action.triggered.connect(self.on_play)
        test_level_action.setWhatsThis("Opens an emulator with the current Level set to 1-1.\nSee Settings.")

        self.level_menu.addSeparator()

        self.place_level_action = self.level_menu.addAction("Place Level on Map")
        self.place_level_action.setIcon(icon("map-pin.svg"))
        self.place_level_action.triggered.connect(self.on_place_level)

        self.reload_action = self.level_menu.addAction("Reload Level")
        self.reload_action.setIcon(icon("refresh-cw.svg"))
        self.reload_action.triggered.connect(self.reload_level)

        self.level_menu.addSeparator()

        self.edit_header_action = self.level_menu.addAction("Level Header")
        self.edit_header_action.setIcon(icon("tool.svg"))
        self.edit_header_action.triggered.connect(self.on_header_editor)

        self.edit_level_settings_action = self.level_menu.addAction("Other Level Settings")
        self.edit_level_settings_action.setIcon(icon("settings.svg"))
        self.edit_level_settings_action.triggered.connect(self.on_edit_level_settings)

        self.level_menu.addSeparator()

        self.close_level_action = self.level_menu.addAction("Close Level")
        self.close_level_action.setIcon(icon("x.svg"))
        self.close_level_action.triggered.connect(self.close_current_level)

        self.menuBar().addMenu(self.level_menu)

        self._rom_menu = RomMenu(self.level_ref)
        self._rom_menu.needs_gui_refresh.connect(self.enable_disable_gui_elements)
        self.menuBar().addMenu(self._rom_menu)

        self.context_menu = LevelContextMenu(self.level_ref)
        self.context_menu.triggered.connect(self.on_menu)

        self.level_view = LevelView(self, self.level_ref, self.settings, self.context_menu)

        # TODO: make into an editor setting
        self.level_view.zoom_in()

        self.view_menu = ViewMenu(self.level_view)

        self.menuBar().addMenu(self.view_menu)

        help_menu = HelpMenu(self)
        self.menuBar().addMenu(help_menu)

        self.debug_menu = None

        if is_nightly_version() or not is_pyinstalled():
            self._add_debug_menu()

        #
        # Other widgets
        #

        self.undo_stack.indexChanged.connect(self._on_level_data_changed)
        self.undo_stack.cleanChanged.connect(self._on_level_data_changed)

        self.scroll_panel = QScrollArea()
        self.scroll_panel.setWidgetResizable(True)
        self.scroll_panel.setWidget(self.level_view)

        self.setCentralWidget(self.scroll_panel)

        self.spinner_panel = SpinnerPanel(self, self.level_ref)
        self.spinner_panel.zoom_in_triggered.connect(self.level_view.zoom_in)
        self.spinner_panel.zoom_out_triggered.connect(self.level_view.zoom_out)
        self.spinner_panel.object_change.connect(self.on_spin)

        self.object_list = ObjectList(self, self.level_ref, self.context_menu)
        self.object_list.selection_changed.connect(self.level_view.scroll_to_objects)

        self.object_dropdown = ObjectDropdown(self)
        self.object_dropdown.object_selected.connect(self._on_placeable_object_selected)

        self.level_size_bar = LevelSizeBar(self, self.level_ref)
        self.enemy_size_bar = EnemySizeBar(self, self.level_ref)

        size_and_palette = QWidget()
        size_and_palette.setLayout(QHBoxLayout())
        size_and_palette.layout().setContentsMargins(0, 0, 0, 0)

        size_layout = QVBoxLayout()
        size_layout.addWidget(self.level_size_bar)
        size_layout.addWidget(self.enemy_size_bar)

        size_and_palette.layout().addLayout(size_layout, stretch=1)
        size_and_palette.layout().addWidget(SidePalette(self.level_ref))

        self.jump_list = JumpList(self, self.level_ref)
        self.jump_list.add_jump.connect(self.on_jump_added)
        self.jump_list.edit_jump.connect(self.on_jump_edit)
        self.jump_list.remove_jump.connect(self.on_jump_removed)

        jump_buttons = QWidget()
        jump_buttons.setLayout(QHBoxLayout())
        jump_buttons.layout().setContentsMargins(0, 0, 0, 0)

        add_jump_button = QPushButton("Add Jump")
        add_jump_button.clicked.connect(self.on_jump_added)

        set_jump_destination_button = QPushButton("Set Jump Destination")
        set_jump_destination_button.clicked.connect(self._show_jump_dest)

        jump_buttons.layout().addWidget(add_jump_button)
        jump_buttons.layout().addWidget(set_jump_destination_button)

        splitter = QSplitter(self)
        splitter.setOrientation(Qt.Orientation.Vertical)

        splitter.addWidget(self.object_list)
        splitter.setStretchFactor(0, 1)
        splitter.addWidget(self.jump_list)
        splitter.addWidget(jump_buttons)

        splitter.setChildrenCollapsible(False)

        self.level_toolbar = QToolBar("Level Info Toolbar", self)
        self.level_toolbar.setContextMenuPolicy(Qt.ContextMenuPolicy.PreventContextMenu)
        self.level_toolbar.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.level_toolbar.setOrientation(Qt.Orientation.Horizontal)
        self.level_toolbar.setFloatable(False)

        self.level_toolbar.addWidget(self.spinner_panel)
        self.level_toolbar.addWidget(self.object_dropdown)
        self.level_toolbar.addWidget(size_and_palette)
        self.level_toolbar.addWidget(splitter)

        self.level_toolbar.setAllowedAreas(Qt.ToolBarArea.LeftToolBarArea | Qt.ToolBarArea.RightToolBarArea)

        self.addToolBar(Qt.ToolBarArea.RightToolBarArea, self.level_toolbar)

        self.object_toolbar = ObjectToolBar(self)
        self.object_toolbar.object_selected.connect(self._on_placeable_object_selected)

        object_toolbar = QToolBar("Object Toolbar", self)
        object_toolbar.setContextMenuPolicy(Qt.ContextMenuPolicy.PreventContextMenu)
        object_toolbar.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        object_toolbar.setFloatable(False)

        object_toolbar.addWidget(self.object_toolbar)
        object_toolbar.setAllowedAreas(Qt.ToolBarArea.LeftToolBarArea | Qt.ToolBarArea.RightToolBarArea)

        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, object_toolbar)

        self.menu_toolbar = QToolBar("Menu Toolbar", self)
        self.menu_toolbar.setOrientation(Qt.Orientation.Horizontal)
        self.menu_toolbar.setIconSize(TOOLBAR_ICON_SIZE)

        self.menu_toolbar.addAction(self.file_menu.settings_action)

        self.menu_toolbar.addSeparator()

        self.menu_toolbar.addAction(self.file_menu.open_rom_action)
        self.menu_toolbar.addAction(self.file_menu.save_rom_action)

        self.menu_toolbar.addSeparator()

        self.menu_toolbar.addAction(self._rom_menu.rom_settings_action)
        self.menu_toolbar.addAction(self._rom_menu.game_properties_action)

        self.menu_toolbar.addSeparator()

        self.menu_toolbar.addAction(self.select_level_action)

        self.menu_toolbar.addSeparator()

        self.menu_toolbar.addAction(self.undo_action)
        self.menu_toolbar.addAction(self.redo_action)

        self.menu_toolbar.addSeparator()

        self.menu_toolbar.addAction(test_level_action)

        self.menu_toolbar.addSeparator()

        self.zoom_out_action = self.menu_toolbar.addAction(icon("zoom-out.svg"), "Zoom Out")
        self.zoom_out_action.triggered.connect(self.level_view.zoom_out)

        self.zoom_in_action = self.menu_toolbar.addAction(icon("zoom-in.svg"), "Zoom In")
        self.zoom_in_action.triggered.connect(self.level_view.zoom_in)

        self.menu_toolbar.addSeparator()

        self.menu_toolbar.addAction(self.edit_header_action)
        self.edit_header_action.setWhatsThis(
            "<b>Header Editor</b><br/>"
            "Many configurations regarding the level are done in its header, like the length of "
            "the timer, or where and how Mario enters the level.<br/>"
        )

        self.menu_toolbar.addAction(self.edit_level_settings_action)

        self.jump_destination_action = self.menu_toolbar.addAction(
            icon("arrow-right-circle.svg"), "Go to Jump Destination"
        )
        self.jump_destination_action.triggered.connect(self._go_to_jump_destination)
        self.jump_destination_action.setWhatsThis(
            "Opens the level, that can be reached from this one, e.g. by entering a pipe."
        )

        self.menu_toolbar.addSeparator()

        self.menu_toolbar.addAction(help_menu.whats_this_action)

        self.menu_toolbar.addSeparator()
        self.warning_list = WarningList(self, self.level_ref, self.level_view, self.object_list)

        warning_action = self.menu_toolbar.addAction(icon("alert-triangle.svg"), "Warning Panel")
        warning_action.setWhatsThis("Shows a list of warnings.")
        warning_action.triggered.connect(self.warning_list.show)
        warning_action.setDisabled(True)

        self.warning_list.warnings_updated.connect(warning_action.setEnabled)

        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.menu_toolbar)

        self.status_bar = ObjectStatusBar(self, self.level_ref)
        self.setStatusBar(self.status_bar)

        self.delete_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Delete), self, self._on_delete_key)

        QShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_D), self, self._add_debug_menu)

        QShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_X), self, self._cut_objects)
        QShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_C), self, self._copy_objects)
        QShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_V), self, self._paste_objects)

        self.undo_action.setShortcut(Qt.Modifier.CTRL | Qt.Key.Key_Z)
        self.redo_action.setShortcuts(
            [Qt.Modifier.CTRL | Qt.Key.Key_Y, Qt.Modifier.CTRL | Qt.Modifier.SHIFT | Qt.Key.Key_Z]
        )

        QShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_Plus), self, self.level_view.zoom_in)
        QShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_Minus), self, self.level_view.zoom_out)

        QShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_A), self, self.level_view.select_all)
        QShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_L), self, self.object_dropdown.setFocus)

        self.rom_content_changed.connect(self._on_rom_changed_externally)

        self.check_for_update_on_startup()

        self.showMaximized()

    def _add_debug_menu(self):
        if self.debug_menu:
            return

        self.debug_menu = DebugMenu()
        self.menuBar().addMenu(self.debug_menu)

    def on_new_level(self, dont_check=False):
        if not dont_check and not self.safe_to_change():
            return

        object_set = ObjectSetSelector.get_object_set(self, alternative_title="Creating New Level")

        if object_set == -1:
            # was cancelled
            return

        self._reload_rom()

        self.level_ref.level = Level(f"New {OBJECT_SET_NAMES[object_set]} Level", object_set_number=object_set)

        minimal_level_header = bytearray([0, 0, 0, 0, 0, 0, 0x81, object_set, 0])
        self.level_ref.level.from_bytes(object_data=(0, minimal_level_header), enemy_data=(0, bytearray()))

        self.level_ref.level_changed.emit()

    def _reload_rom(self):
        try:
            ROM.reload_from_file()
        except FileNotFoundError:
            self._on_rom_not_found(ROM.path)
            raise

    def _on_rom_not_found(self, path: str):
        QMessageBox.critical(
            self,
            "ROM not found",
            f"Could not find ROM at '{path}'.\n\nIt was either deleted or never existed in the first place.",
        )

    def _on_level_data_changed(self):
        level_is_not_attached = self.level_ref.level and not self.level_ref.level.attached_to_rom
        changes_were_made = not self.undo_stack.isClean() or PaletteGroup.changed

        if self.level_ref:
            self._update_block_graphics_in_ui()

        self.file_menu.save_rom_action.setEnabled(level_is_not_attached or changes_were_made)

        self.jump_destination_action.setEnabled(bool(self.level_ref.level and self.level_ref.level.has_next_area))

        self._save_auto_data()

    def _on_show_settings(self):
        SettingsDialog(self.settings, self).exec()

    def _on_want_to_reload_rom(self):
        self.hotswap_roms()
        self._update_accepted_hash()

    def _on_rom_changed_externally(self):
        self._rom_watcher_enabled = False

        wants_to_reload_rom = (
            self.settings.value("editor/monitor_rom_for_changes")
            and QMessageBox.information(
                self,
                "ROM Changed",
                "The ROM has been changed externally.\n\n"
                "You can have Foundry open the new ROM and try to apply your current changes to it. Or you can ignore "
                "the external changes. NotE that those will be lost, if you save in Foundry afterwards.",
                QMessageBox.StandardButton.Ignore | QMessageBox.StandardButton.Apply,
            )
            == QMessageBox.StandardButton.Apply
        )

        if wants_to_reload_rom:
            self.hotswap_roms()

        self._update_accepted_hash()
        self._rom_watcher_enabled = True

    @staticmethod
    def _save_auto_rom():
        ROM.save_to_file(auto_save_rom_path, set_new_path=False)

    def _save_auto_data(self):
        if not self.level_ref:
            return

        (object_offset, object_bytes), (
            enemy_offset,
            enemy_bytes,
        ) = self.level_ref.level.to_bytes()

        object_set_number = self.level_ref.level.object_set_number

        object_data = base64.b64encode(object_bytes).decode("ascii")
        enemy_data = base64.b64encode(enemy_bytes).decode("ascii")

        data_dict = {
            "object_set_number": object_set_number,
            "object_address": object_offset,
            "object_data": object_data,
            "enemy_address": enemy_offset,
            "enemy_data": enemy_data,
        }

        Path(auto_save_level_data_path).write_text(json.dumps(data_dict))

    def _load_auto_save(self):
        # rom already loaded
        data_dict = json.loads(Path(auto_save_level_data_path).read_text())

        object_address = data_dict["object_address"]
        object_data = bytearray(base64.b64decode(data_dict["object_data"]))
        enemy_address = data_dict["enemy_address"]
        enemy_data = bytearray(base64.b64decode(data_dict["enemy_data"]))
        object_set_number = data_dict["object_set_number"]
        # TODO add world number here
        # TODO since we know the addresses of the level, why not automatically attach it, if we still can?

        # load level from ROM, or from m3l file
        if object_address == enemy_address == 0:
            if not auto_save_m3l_path.exists():
                QMessageBox.critical(
                    self,
                    "Failed loading auto save",
                    "Could not recover m3l file, that was edited, when the editor crashed.",
                )

            self.load_m3l(auto_save_m3l_path)
        else:
            self.update_level("recovered level", object_address, enemy_address, object_set_number)
            self.level_ref.level.from_bytes((object_address, object_data), (enemy_address, enemy_data), True)

    def _go_to_jump_destination(self):
        if not self.safe_to_change():
            return

        level_address = self.level_ref.level.next_area_objects
        enemy_address = self.level_ref.level.next_area_enemies
        object_set = self.level_ref.level.next_area_object_set_no
        old_world = self.level_ref.level.world

        world, level = world_and_level_for_level_address(level_address + HEADER_LENGTH)

        self._reload_rom()

        if world == -1:
            new_world = old_world
        else:
            new_world = world

        self.update_level(f"Level {world}-{level}", level_address, enemy_address, object_set, new_world)

    def on_play(self, temp_dir=Path()):
        """
        Copies the ROM, including the current level, to a temporary directory, saves the current level as level 1-1 and
        opens the rom in an emulator.
        """
        temp_dir = Path(tempfile.gettempdir()) / "smb3foundry"
        temp_dir.mkdir(parents=True, exist_ok=True)

        super(FoundryMainWindow, self).on_play(temp_dir)

    def _save_changes_to_instaplay_rom(self, path_to_temp_rom) -> bool:
        temp_rom = ROM.from_file(path_to_temp_rom)

        insta_player = InstaPlayer(temp_rom)

        # TODO: reraise exception with error message to not trigger two error dialogs in a row

        try:
            insta_player.put_current_level_to_level_1_1(self.level_ref.level)

        except CantFindFirstTile as e:
            title = "Couldn't place level"
            message = f"Could not find a level 1 tile in World {e.world} to put your level at."

            QMessageBox.critical(self, title, message)

            return False

        except LevelNotAttached:
            title = "Couldn't place level"
            message = "The Level is not part of the rom yet (M3L?). Try saving it into the ROM first."

            QMessageBox.critical(self, title, message)

            return False

        powerup = POWERUPS[self.settings.value("editor/default_powerup")]
        starman = self.settings.value("editor/powerup_starman")

        insta_player.set_default_powerup(powerup, with_starman=starman)

        if self.settings.value("editor/instaplay_skip_title_screen"):
            insta_player.skip_title_screen()
            insta_player.skip_world_info_box()

        save_all_palette_groups(temp_rom)

        temp_rom.save_to(path_to_temp_rom)

        return True

    def _show_jump_dest(self):
        header_editor = HeaderEditor(self, self.level_ref)
        header_editor.tab_widget.setCurrentIndex(3)

        header_editor.exec()

    def update_title(self):

        level_name = ""
        rom_name = ""
        app_name = "SMB3Foundry "
        version_name = get_current_version_name()

        if not version_name.startswith("nightly"):
            version_name = f"v{version_name}"

        if ROM.is_loaded():
            rom_name = f"{ROM.name} — "

        if self.level_ref:
            if self.level_ref.level.name:
                level_name = self.level_view.level_ref.name
            else:
                level_name = f"{OBJECT_SET_NAMES[self.level_ref.object_set_number]} Level"

            level_name += " — "

        self.setWindowTitle(level_name + rom_name + f"{app_name} {version_name}")

    def on_open_rom(
        self, path_to_rom=Path(), check_for_asm_files=True, close_current_level=True, try_opening_level=True
    ):
        if not self.safe_to_change():
            return

        if not path_to_rom.is_file() and not (path_to_rom := self._ask_for_path_to_rom()).is_file():
            self.enable_disable_gui_elements()

            return

        # Proceed to load the file chosen by the user
        try:
            ROM.load_from_file(path_to_rom, reset_globals=False)
            self.set_rom_path_to_watch(path_to_rom)

            if close_current_level:
                self.close_current_level()

            if check_for_asm_files:
                # TODO check for file and input errors for this separately
                self._check_for_asm_fns_imports(path_to_rom)

            if self.settings.value("editor/ask_for_level_management"):
                self._ask_for_level_management()

            self._check_for_refresh()

        except FileNotFoundError:
            self._on_rom_not_found(path_to_rom)
            return

        except IOError as exp:
            QMessageBox.warning(self, type(exp).__name__, f"Cannot open file '{path_to_rom}'.")
            return

        finally:
            self.enable_disable_gui_elements()

        if path_to_rom == auto_save_rom_path:
            self._load_auto_save()

        else:
            self._save_auto_rom()

        self.enable_disable_gui_elements()

        if try_opening_level:
            if not self.open_level_selector(None):
                self.on_new_level(dont_check=True)

    def _check_for_asm_fns_imports(self, path_to_rom: str | Path):
        if self.settings.value("editor/asm_loading_behavior") == ASMLoadingBehavior.DONT_ASK:
            ROM.reset_globals()
            return

        asm_path, fns_path = asm_paths_from_rom_path(Path(path_to_rom).parent)

        load_without_asking = self.settings.value("editor/asm_loading_behavior") == ASMLoadingBehavior.LOAD_IF_AVAILABLE
        files_exist = asm_path.exists() and fns_path.exists()
        incompatibility_found = self._has_found_incompatibilities()

        # lwa fe inc
        #   0  0   0  dont_load
        #   0  0   1  ask_inc
        #   0  1   0  ask_found
        #   0  1   1  ask_inc
        #   1  0   0  dont_load
        #   1  0   1  ask_inc
        #   1  1   0  just load
        #   1  1   1  just load

        dont_load = not files_exist and not incompatibility_found

        if dont_load:
            return

        just_load = load_without_asking and files_exist

        ask_inc = not just_load and incompatibility_found
        ask_found = not load_without_asking and files_exist and not incompatibility_found

        query_paths = False

        if ask_inc:
            answer = QMessageBox.question(
                self,
                "Incompatibilities found",
                "The data in your ROM differs from expected values. This is likely due to code changes.\n\n"
                "If you compiled your own ROM, supplying additional ASM files can solve this issue. Do you want "
                "to import them now?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            query_paths = answer == QMessageBox.StandardButton.Yes

        elif ask_found:
            answer = QMessageBox.question(
                self,
                "ASM files found",
                "There were files in your ROM directory, that look like ASM files.\n\n"
                "If you compiled your own ROM, perhaps you want to load those into the editor as well?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            query_paths = answer == QMessageBox.StandardButton.Yes

        if not just_load and not query_paths:
            return

        if just_load:
            self.file_menu.update_globals_from_fns(asm_path, fns_path)

        elif query_paths:
            self.file_menu.on_fns_import()

    @staticmethod
    def _has_found_incompatibilities():
        """
        Checks if code at certain addresses in the ROM has changed. Those addresses are important values and look up
        tables used in drawing levels. If they don't match, it is likely, that code has been moved and the editor would
        read in wrong data.

        Expected data is taken from a vanilla US rom.
        """
        addresses_and_expected_data = (
            (Constants.COMPLETABLE_TILES_LIST, bytearray(b"P\xe8\xe6\xbd\xe0\x00\x01@A\x80")),
            (Constants.LAYOUT_LIST_OFFSET, bytearray(b"\xaa\xa5;\xa6\\\xa7\r\xa9.\xaa")),
            (Constants.LEVELS_IN_WORLD_LIST_OFFSET, bytearray(b"|\xb4f\xb5\x98\xb6\x8c\xb7|\xb8")),
            (Constants.LEVEL_BASE_OFFSET, bytearray(b"\xff\x00\x01\x02\x03\x04\x05\x06\x07\x08")),
            (Constants.LEVEL_ENEMY_LIST_OFFSET, bytearray(b"R\xb4\x08\xb50\xb6H\xb7(\xb8")),
            (Constants.LEVEL_X_POS_LISTS, bytearray(b"=\xb4\xd9\xb4\xfc\xb5&\xb7\xfe\xb7")),
            (Constants.LEVEL_Y_POS_LISTS, bytearray(b"(\xb4\xaa\xb4\xc8\xb5\x04\xb7\xd4\xb7")),
            (Constants.OFFSET_BY_OBJECT_SET_A000, bytearray(b"\x0b\x0f\x15\x10\x11\x13\x12\x12\x12\x14")),
            (Constants.OFFSET_BY_OBJECT_SET_C000, bytearray(b"\n\x0e\x0e\x0e\x0e\x0e\x0e\x0e\x0e\x0e")),
            (Constants.SPECIAL_ENTERABLE_TILES_LIST, bytearray(b"P\xe8\xbc\xe0\xc9_\xdff\xbd\xe6")),
            (Constants.STRUCTURE_DATA_OFFSETS, bytearray(b"$\xb4\xa6\xb4\xc4\xb5\x00\xb7\xd0\xb7")),
            (Constants.TILE_ATTRIBUTES_TS0_OFFSET, bytearray(b"\x03g\xbf\xe9\x03g\xbf\xe9 \x0e")),
            (Constants.TSA_OS_LIST, bytearray(b"\x0b\x0f\x15\x10\x11\x13\x12\x12\x12\x14")),
            (Constants.LEVEL_LOAD_ROUTINE_BY_OBJECT_SET, bytearray(b"\xad\n\x07 \x99\xfe\x08\xa4\x08\xa4")),
        )

        for address, expected_data in addresses_and_expected_data:
            if ROM().read(address, len(expected_data)) != expected_data:
                return True
        else:
            return False

    @staticmethod
    def _rom_has_asm_files_in_path(rom_path: Path):
        containing_dir = rom_path.parent

        has_asm_file = bool(list(containing_dir.glob("*.asm")))
        has_fns_file = bool(list(containing_dir.glob("*.fns")))

        return has_asm_file and has_fns_file

    def _ask_for_path_to_rom(self):
        # otherwise, ask the user what new file to open
        path_to_rom, _ = QFileDialog.getOpenFileName(
            self,
            caption="Open ROM",
            dir=self.settings.value("editor/default_dir_path"),
            filter=ROM_FILE_FILTER,
        )

        return Path(path_to_rom)

    def on_open_m3l(self, _):
        if not self.safe_to_change():
            return

        # otherwise, ask the user what new file to open
        if not (pathname := load_m3l_filename(self.settings.value("editor/default_dir_path"))):
            return

        self._reload_rom()

        self.load_m3l(pathname)
        save_m3l(auto_save_m3l_path, self.level_ref.level.to_m3l())

    def load_m3l(self, pathname: Path | str):
        if not self._ask_for_palette_save():
            return

        if self.level_ref.level is None:
            self.level_ref.level = Level()

        load_m3l(pathname, self.level_ref.level)

    def safe_to_change(self) -> bool:
        return super(FoundryMainWindow, self).safe_to_change() and self._ask_for_palette_save()

    def on_save_rom(self, _):
        self.try_saving_rom(False)

    def on_save_rom_as(self, _):
        self.try_saving_rom(True)

    def _ask_for_level_management(self):
        if ROM.additional_data.managed_level_positions is not None:
            return

        answer = QMessageBox.question(
            NO_PARENT,
            "Automatic Level Management Feature",
            "Levels of the same type are stored in the same area of the ROM. If you add new objects to a Level, you "
            "might overwrite the Level, that comes right after it in memory.\n\n"
            "Foundry can parse your ROM and find all Levels accessible to the player (!). That way, when you extend a "
            "Level, Foundry can automatically move the Levels, so that this doesn't happen and so that you can use as "
            "much memory as is available for that type of Level.\n\n"
            "This can also be (de-)activated under 'Rom Settings' later.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Ignore,
        )

        if answer == QMessageBox.StandardButton.Ignore:
            return

        if answer == QMessageBox.StandardButton.Yes:
            if not self._found_level_load_code():
                return

            ROM.additional_data.managed_level_positions = True
            self._parse_levels_in_rom()

    def _found_level_load_code(self):
        # TODO ask to put add the fns file instead
        expected_data = bytearray(b"\xad\n\x07 \x99\xfe\x08\xa4\x08\xa4")

        found_data = ROM().read(Constants.LEVEL_LOAD_ROUTINE_BY_OBJECT_SET, len(expected_data))

        if found_data != expected_data:
            QMessageBox.warning(
                self,
                "Automatic Level Management Feature",
                "The ROM was changed in a way that makes this feature unavailable. "
                "LevelLoad_ByTileset was not where we expected it.",
            )

        return found_data == expected_data

    @staticmethod
    def _parse_levels_in_rom():
        pd = LevelParseProgressDialog()

        if pd.wasCanceled():
            ROM.additional_data.managed_level_positions = None
            return

        ROM.additional_data.found_levels = [pd.levels_by_address[key] for key in sorted(pd.levels_by_address.keys())]

        lo = LevelOrganizer(ROM(), ROM().additional_data.found_levels)
        lo.rearrange_levels()
        lo.rearrange_enemies()

        ROM.save_to_file(ROM.path)

    def _check_for_refresh(self):
        """Scribe can move around levels, so we would need to read them in again."""
        if not ROM.additional_data.needs_refresh:
            return

        answer = QMessageBox.question(
            self,
            "External Changes to Levels detected",
            "We detected changes to where Levels are saved from a different source (probably SMB3 Scribe). We need to "
            "parse the ROM again to update the locations of the moved Levels.\n\n"
            "If you choose 'No', then the Found Level information will be deleted, but you can still select Levels "
            "through the world maps in the Level Selector, as before.\n\n"
            "Reparse the Levels?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        ROM.additional_data.found_levels.clear()
        ROM.additional_data.needs_refresh = False

        ROM.additional_data.managed_level_positions = answer == QMessageBox.StandardButton.Yes

        if ROM.additional_data.managed_level_positions:
            self._parse_levels_in_rom()

    def _ask_for_palette_save(self) -> bool:
        """
        If Object Palettes have been changed, this function opens a dialog box, asking the user, if they want to save
        the changes, dismiss them, or cancel whatever they have been doing (probably saving/selecting another level).

        Saving or restoring Object Palettes is done inside the function if necessary.

        :return: False, if Cancel was chosen. True, if Palettes were restored or saved to ROM.
        """
        if not PaletteGroup.changed:
            return True

        answer = QMessageBox.question(
            self,
            "Please confirm",
            "You changed some object palettes. This is a change, that potentially affects other levels in this ROM. Do "
            "you want to save these changes, or restore the defaults and continue?",
            QMessageBox.Cancel | QMessageBox.RestoreDefaults | QMessageBox.Save,
            QMessageBox.Cancel,
        )

        if answer == QMessageBox.Cancel:
            return False

        if answer == QMessageBox.Save:
            save_all_palette_groups()
            self._write_to_rom(ROM.path, False)

        elif answer == QMessageBox.RestoreDefaults:
            restore_all_palettes()
            self.level_ref.level.reload()

        return True

    def try_saving_rom(self, is_save_as):
        safe_to_save, reason, additional_info = self.level_view.level_safe_to_save()

        if not safe_to_save:
            answer = QMessageBox.warning(
                self,
                reason,
                f"{additional_info}\n\nDo you want to proceed?",
                QMessageBox.No | QMessageBox.Yes,
                QMessageBox.No,
            )

            if answer == QMessageBox.No:
                return

        if self.level_ref and not self.level_ref.attached_to_rom:
            QMessageBox.information(
                self,
                "Importing M3L into ROM",
                "You are currently editing a level stored in an m3l file outside of the ROM. Please select the "
                "positions in the ROM you want the level objects and enemies/items to be stored.",
                QMessageBox.Ok,
            )

            if not self._ask_for_palette_save():
                return

            if not self.on_place_level():
                return

            if is_save_as:
                # if we save to another rom, don't consider the level
                # attached (to the current rom)
                attach_cmd = self.undo_stack.command(self.undo_stack.index() - 1)
                attach_cmd.setObsolete(True)

                self.undo_stack.undo()
            else:
                # the m3l is saved to the current ROM, we can get rid of the auto save
                auto_save_m3l_path.unlink(missing_ok=True)

        else:
            if not self._ask_for_palette_save():
                return

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

        if str(pathname) == str(auto_save_rom_path):
            QMessageBox.critical(
                self,
                "Cannot save to auto save ROM",
                "You can't save to the auto save ROM, as it will be deleted, when exiting the editor. Please choose "
                "another location, or your changes will be lost.",
            )

            return

        self._rom_watcher_enabled = False

        if self._save_current_changes_to_file(pathname, set_new_path=True) and not is_save_as:
            self.undo_stack.setClean()

            # Make sure the rom file watcher goes off right now, so it ignores the change
            QApplication.processEvents()

        self._rom_watcher_enabled = True

        self.update_title()

    def on_import_enemies_from_asm(self):
        if not (pathname := load_asm_filename("Enemy ASM", self.settings.value("editor/default_dir_path"))):
            return

        self.undo_stack.push(ImportASMEnemies(self.level_ref, pathname))

    def _attach_to_rom(self, object_data_offset: int, enemy_data_offset: int):
        if 0x0 in [object_data_offset, enemy_data_offset]:
            raise ValueError("You cannot save level or enemy data to the beginning of the ROM (address 0x0).")

        self.undo_stack.push(AttachLevelToRom(self.level_ref, object_data_offset, enemy_data_offset))

    def _save_current_changes_to_file(self, pathname: str, set_new_path: bool):
        try:
            return super(FoundryMainWindow, self)._save_current_changes_to_file(pathname, set_new_path)
        finally:
            self._save_auto_rom()

    def on_menu(self, action: QAction):
        pos = self.level_view.mapFromGlobal(self.context_menu.get_position())

        if action is self.context_menu.remove_action:
            self.remove_selected_objects()
        elif action is self.context_menu.add_object_action:
            selected_object = self.object_dropdown.currentIndex()

            if selected_object != -1:
                self.place_object_from_dropdown(pos)
            else:
                self.add_object_at(pos)
        elif action is self.context_menu.grab_selected_object_action:
            assert self.context_menu.object_to_grab is not None

            self.object_toolbar.select_object(self.context_menu.object_to_grab)
            self.object_dropdown.select_object(self.context_menu.object_to_grab)
        elif action is self.context_menu.cut_action:
            self._cut_objects()
        elif action is self.context_menu.copy_action:
            self._copy_objects()
        elif action is self.context_menu.paste_action:
            self._paste_objects(pos)
        elif action is self.context_menu.into_foreground_action:
            self.bring_objects_to_foreground()
        elif action is self.context_menu.into_background_action:
            self.bring_objects_to_background()

        self.level_view.update()

    def reload_level(self):
        if not self.safe_to_change():
            return

        level_name = self.level_ref.name
        object_data = self.level_ref.header_offset
        enemy_data = self.level_ref.enemy_offset
        object_set = self.level_ref.object_set_number
        world_index = self.level_ref.level.world

        self._reload_rom()

        self.update_level(level_name, object_data, enemy_data, object_set, world_index)

    def on_place_level(self) -> bool:
        if not self.level_ref:
            return False

        level_selector = LevelSelector(self)
        level_selector.goto_world(self.level_ref.level.world)
        level_selector.deactivate_level_list()

        if level_selector.exec() != QMessageBox.Accepted:
            return False

        if (level_pointer := level_selector.clicked_level_pointer) is None:
            QMessageBox.warning(
                self,
                "No Level on Map selected",
                "You need to click a position on a World Map. "
                "If the position you want to use is not clickable, you can save this level as an M3L, "
                "add/move a level pointer to that position in Scribe and try again.",
            )

            return False

        level_pointer.object_set = self.level_ref.level.object_set_number

        if self.level_ref.level.attached_to_rom:
            level_pointer.level_address = self.level_ref.level.layout_address
            level_pointer.enemy_address = self.level_ref.level.enemy_offset - 1
        else:
            self._attach_to_rom(level_selector.object_data_offset, level_selector.enemy_data_offset)

        level_pointer.write_back()

        return True

    def _on_placeable_object_selected(self, level_object: InLevelObject):
        if self.sender() is not self.object_dropdown:
            self.object_dropdown.select_object(level_object)

        if self.sender() is not self.object_toolbar:
            self.object_toolbar.select_object(level_object)

    def bring_objects_to_foreground(self):
        self.undo_stack.push(ToForeground(self.level_ref, self.level_ref.selected_objects))

    def bring_objects_to_background(self):
        self.undo_stack.push(ToBackground(self.level_ref, self.level_ref.selected_objects))

    def add_object_at(self, q_point: QPoint, domain=0, obj_type=0):
        self.undo_stack.push(AddLevelObjectAt(self.level_view, q_point, domain, obj_type))

    def add_enemy_at(self, q_point: QPoint, enemy_type=0x72):
        self.undo_stack.push(AddEnemyAt(self.level_view, q_point, enemy_type))

    def _cut_objects(self):
        self._copy_objects()
        self.remove_selected_objects()

    def _copy_objects(self):
        selected_objects = self.level_view.get_selected_objects().copy()

        if selected_objects:
            self.context_menu.set_copied_objects(selected_objects)

    def _paste_objects(self, q_point: QPoint | None = None):
        if not (copied_objects := self.context_menu.get_copied_objects())[0]:
            return

        copied_level_objects = cast(tuple[list[InLevelObject], Position], copied_objects)

        # clear selection of copied/other previously selected objects, so only the pasted ones are selected
        self.level_view.select_objects([], replace_selection=True)

        self.undo_stack.push(PasteObjectsAt(self.level_view, copied_level_objects, q_point))

    def _on_delete_key(self):
        # if the jump list is focused and a jump is selected, delete it
        if self.focusWidget() is self.jump_list:
            self.jump_list.delete_selected_jump()

            return

        # otherwise simply delete selected objects in the level view
        self.remove_selected_objects()

    def remove_selected_objects(self):
        selected_objects = [obj for obj in self.level_ref.level.get_all_objects() if obj.selected]

        if not selected_objects:
            return

        self.undo_stack.push(RemoveObjects(self.level_ref, selected_objects))

    def on_spin(self, _):
        selected_objects = self.level_ref.selected_objects

        if len(selected_objects) != 1:
            logging.error(selected_objects, RuntimeWarning)
            return

        selected_object = selected_objects[0]

        obj_type = self.spinner_panel.get_type()

        if isinstance(selected_object, LevelObject):
            domain = self.spinner_panel.get_domain()

            if selected_object.is_4byte:
                length = self.spinner_panel.get_length()
            else:
                length = None

            self.undo_stack.push(ReplaceLevelObject(self.level_ref, selected_object, domain, obj_type, length))
        else:
            self.undo_stack.push(ReplaceEnemy(self.level_ref, selected_object, obj_type))

        self.level_ref.data_changed.emit()

    def open_level_selector(self, _):
        if not self.safe_to_change():
            return False

        level_selector = LevelSelector(self)
        if self.level_ref:
            level_selector.goto_world(self.level_ref.level.world)

        level_was_selected = level_selector.exec() == QDialog.DialogCode.Accepted

        if level_was_selected:
            self._reload_rom()

            self.update_level(
                level_selector.level_name,
                level_selector.object_data_offset,
                level_selector.enemy_data_offset,
                level_selector.object_set,
                level_selector.world_index,
            )

        return level_was_selected

    def on_edit_level_settings(self, _):
        LevelSettingsDialog(self, self.level_ref).exec()

    def on_header_editor(self, _):
        HeaderEditor(self, self.level_ref).exec()

    def update_level(
        self,
        level_name: str,
        object_data_offset: LevelAddress,
        enemy_data_offset: EnemyItemAddress,
        object_set: int,
        world_number=-1,
    ):
        try:
            self.level_ref.load_level(level_name, object_data_offset, enemy_data_offset, object_set, world_number)
            self.scroll_panel.horizontalScrollBar().setValue(0)
            self.scroll_panel.verticalScrollBar().setValue(0)

            self.settings.setValue("editor/remember_last_level_path", ROM.path)
            self.settings.setValue("editor/remember_last_level_object_set", object_set)
            self.settings.setValue("editor/remember_last_level_lvl_address", object_data_offset)
            self.settings.setValue("editor/remember_last_level_enemy_address", enemy_data_offset)
            self.settings.setValue("editor/remember_last_level_world_number", self.level_ref.level.world)
        except IndexError:
            QMessageBox.critical(
                self,
                "Please confirm",
                "Failed loading level. The level offsets don't match.",
            )

    def close_current_level(self):
        if not self.safe_to_change():
            return

        self.level_ref.level = None
        if not self._protect_undo_stack:
            self.undo_stack.clear()
        self.enable_disable_gui_elements()

    def update_gui_for_level(self):
        restore_all_palettes()

        if not self._protect_undo_stack:
            self.undo_stack.clear()

        self.enable_disable_gui_elements()

        self.update_title()
        self.jump_list.update()

        is_a_world_map = isinstance(self.level_ref.level, WorldMap)

        self.file_menu.save_m3l_action.setEnabled(not is_a_world_map)
        self.edit_header_action.setEnabled(not is_a_world_map)

        self._update_block_graphics_in_ui()

        if is_a_world_map:
            self.object_dropdown.clear()
            self.object_dropdown.setEnabled(False)

            self.jump_list.setEnabled(False)
            self.jump_list.clear()
        else:
            self.object_dropdown.setEnabled(True)
            self.object_dropdown.set_object_set(
                self.level_ref.object_set_number, self.level_ref.graphic_set, self.level_ref.object_palette_index
            )

            self.jump_list.setEnabled(True)

        self.level_view.update()

    def _update_block_graphics_in_ui(self):
        """Updates the representations of objects in the UI, in case the object set or graphics set changes."""
        self.object_toolbar.set_object_set(
            self.level_ref.object_set_number, self.level_ref.graphic_set, self.level_ref.object_palette_index
        )
        self.object_dropdown.set_object_set(
            self.level_ref.object_set_number, self.level_ref.graphic_set, self.level_ref.object_palette_index
        )

    def enable_disable_gui_elements(self):
        # actions and widgets that depend on whether the ROM is loaded
        rom_elements = [
            # entries in the file menu
            self.file_menu.open_m3l_action,
            self.file_menu.open_level_asm_action,
            self.file_menu.import_enemy_asm_action,
            self.file_menu.save_rom_action,
            self.file_menu.save_rom_as_action,
            self.file_menu.reload_rom_action,
            # entry in the level menu
            self.select_level_action,
            self.new_level_action,
        ]

        rom_elements.extend(self._rom_menu.actions())

        # actions and widgets that depend on whether a level is loaded or not
        level_elements = [
            # entry in the file menu
            self.file_menu.save_m3l_action,
            self.file_menu.save_level_asm_action,
            self.file_menu.export_enemy_asm_action,
            # top toolbar
            self.zoom_out_action,
            self.zoom_in_action,
            # other gui elements
            self.level_view,
            self.level_toolbar,
            self.object_toolbar,
        ]

        level_elements.extend(self.level_menu.actions())
        level_elements.remove(self.select_level_action)
        level_elements.remove(self.new_level_action)
        level_elements.remove(self.undo_action)
        level_elements.remove(self.redo_action)

        level_elements.extend(self.view_menu.actions())

        for gui_element in rom_elements:
            gui_element.setEnabled(ROM.is_loaded())

        for gui_element in level_elements:
            gui_element.setEnabled(ROM.is_loaded() and self.level_ref.fully_loaded)

        self.file_menu.import_enemy_asm_action.setEnabled(bool(self.level_ref))

        if self.level_ref:
            self.reload_action.setEnabled(self.level_ref.level.attached_to_rom)

            self.level_size_bar.update()
            self.enemy_size_bar.update()

        self._on_level_data_changed()

    def on_jump_edit(self):
        index = self.jump_list.currentIndex().row()

        updated_jump = JumpEditor.edit_jump(self, self.level_view.level_ref.jumps[index])

        self.on_jump_edited(updated_jump)

    def on_jump_added(self):
        self.undo_stack.push(AddJump(self.level_ref))

    def on_jump_removed(self):
        self.undo_stack.push(RemoveJump(self.level_ref, self.jump_list.currentIndex().row()))

    def on_jump_edited(self, new_jump: Jump):
        index = self.jump_list.currentIndex().row()

        assert index >= 0

        if not isinstance(self.level_ref.level, Level):
            return

        old_jump = self.level_ref.level.jumps[index]

        if old_jump.to_bytes() == new_jump.to_bytes():
            return

        make_macro(
            self.undo_stack,
            f"Editing {old_jump}",
            RemoveJump(self.level_ref, index),
            AddJump(self.level_ref, new_jump, index),
        )

        self.jump_list.item(index).setText(str(new_jump))

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.MiddleButton:
            if event.buttons() != Qt.MouseButton.NoButton:
                # avoid accidental middle mouse clicks while dragging or resizing
                return

            pos = self.level_view.mapFromGlobal(self.mapToGlobal(event.position().toPoint()))

            self.place_object_from_dropdown(pos)

        if event.button() == Qt.MouseButton.BackButton:
            self.undo_stack.undo()

        if event.button() == Qt.MouseButton.ForwardButton:
            self.undo_stack.redo()

    def place_object_from_dropdown(self, q_point: QPoint) -> None:
        # the dropdown is synchronized with the toolbar, so it doesn't matter where to take it from
        in_level_object = self.object_dropdown.currentData(Qt.ItemDataRole.UserRole)

        self.object_toolbar.add_recent_object(in_level_object)

        if isinstance(in_level_object, LevelObject):
            self.add_object_at(q_point, in_level_object.domain, in_level_object.obj_index)
        elif isinstance(in_level_object, EnemyItem):
            self.add_enemy_at(q_point, in_level_object.obj_index)

        self.level_ref.level.data_changed.emit()

    def closeEvent(self, event: QCloseEvent):
        super(FoundryMainWindow, self).closeEvent(event)

        if not event.isAccepted():
            return

        self._rom_menu.close_everything()

        auto_save_rom_path.unlink(missing_ok=True)
        auto_save_m3l_path.unlink(missing_ok=True)
        auto_save_level_data_path.unlink(missing_ok=True)
