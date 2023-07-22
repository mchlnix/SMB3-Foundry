import base64
import json
import logging
import tempfile
from pathlib import Path
from typing import Optional, cast

from PySide6.QtCore import QPoint, QSize
from PySide6.QtGui import (
    QAction,
    QCloseEvent,
    QKeySequence,
    QMouseEvent,
    QShortcut,
    QUndoStack,
    Qt,
)
from PySide6.QtWidgets import (
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
    QWhatsThis,
    QWidget,
)

from foundry import (
    ROM_FILE_FILTER,
    auto_save_level_data_path,
    auto_save_m3l_path,
    auto_save_rom_path,
    icon,
)
from foundry.features.instaplay import CantFindFirstTile, InstaPlayer, LevelNotAttached
from foundry.game.File import ROM
from foundry.game.additional_data import LevelOrganizer
from foundry.game.gfx import restore_all_palettes
from foundry.game.gfx.Palette import PaletteGroup, save_all_palette_groups
from foundry.game.gfx.objects import EnemyItem, Jump, LevelObject
from foundry.game.gfx.objects.in_level.in_level_object import InLevelObject
from foundry.game.level import EnemyItemAddress, LevelAddress
from foundry.game.level.Level import Level, world_and_level_for_level_address
from foundry.game.level.WorldMap import WorldMap
from foundry.gui.ContextMenu import LevelContextMenu
from foundry.gui.JumpList import JumpList
from foundry.gui.LevelParseProgressDialog import LevelParseProgressDialog
from foundry.gui.LevelSelector import LevelSelector
from foundry.gui.LevelView import LevelView
from foundry.gui.MainWindow import MainWindow
from foundry.gui.ObjectDropdown import ObjectDropdown
from foundry.gui.ObjectList import ObjectList
from foundry.gui.ObjectSetSelector import ObjectSetSelector
from foundry.gui.ObjectStatusBar import ObjectStatusBar
from foundry.gui.ObjectToolBar import ObjectToolBar
from foundry.gui.SpinnerPanel import SpinnerPanel
from foundry.gui.WarningList import WarningList
from foundry.gui.asm import load_asm_filename
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
from foundry.gui.dialogs import HeaderEditor, JumpEditor, SettingsDialog, SidePalette
from foundry.gui.dialogs.SettingsDialog import POWERUPS
from foundry.gui.level_settings.level_settings_dialog import LevelSettingsDialog
from foundry.gui.m3l import load_m3l, load_m3l_filename, save_m3l
from foundry.gui.menus.file_menu import FileMenu
from foundry.gui.menus.help_menu import HelpMenu
from foundry.gui.menus.rom_menu import RomMenu
from foundry.gui.menus.view_menu import ViewMenu
from foundry.gui.settings import Settings
from foundry.gui.widgets.EnemySizeBar import EnemySizeBar
from foundry.gui.widgets.LevelSizeBar import LevelSizeBar
from smb3parse.data_points import Position
from smb3parse.levels import HEADER_LENGTH
from smb3parse.objects.object_set import OBJECT_SET_NAMES

TOOLBAR_ICON_SIZE = QSize(20, 20)


class FoundryMainWindow(MainWindow):
    def __init__(self, path_to_rom=""):
        super(FoundryMainWindow, self).__init__()

        self.settings = Settings("mchlnix", "foundry")

        self.level_ref.level_changed.connect(self.update_gui_for_level)

        self.setWindowIcon(icon("foundry.ico"))
        self.setStyleSheet(self.settings.value("editor/gui_style"))

        self.undo_stack = QUndoStack(self)
        self.undo_stack.setObjectName("undo_stack")

        self.file_menu = FileMenu(self.level_ref, self.settings)

        self.file_menu.open_rom_action.triggered.connect(self.on_open_rom)
        self.file_menu.open_m3l_action.triggered.connect(self.on_open_m3l)
        self.file_menu.save_rom_action.triggered.connect(self.on_save_rom)
        self.file_menu.save_rom_as_action.triggered.connect(self.on_save_rom_as)
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
        self.new_level_action.triggered.connect(self._on_new_level)

        self.select_level_action = self.level_menu.addAction("Select New Level")
        self.select_level_action.setIcon(icon("globe.svg"))
        self.select_level_action.triggered.connect(self.open_level_selector)

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

        self.edit_level_settings = self.level_menu.addAction("Other Level Settings")
        self.edit_level_settings.setIcon(icon("settings.svg"))
        self.edit_level_settings.triggered.connect(self.on_edit_level_settings)

        self.level_menu.addSeparator()

        self.close_level_action = self.level_menu.addAction("Close Level")
        self.close_level_action.setIcon(icon("x.svg"))
        self.close_level_action.triggered.connect(self.close_level)

        self.menuBar().addMenu(self.level_menu)

        self._rom_menu = RomMenu(self.level_ref)
        self._rom_menu.needs_gui_refresh.connect(self._enable_disable_gui_elements)
        self.menuBar().addMenu(self._rom_menu)

        self.context_menu = LevelContextMenu(self.level_ref)
        self.context_menu.triggered.connect(self.on_menu)

        self.level_view = LevelView(self, self.level_ref, self.settings, self.context_menu)

        self.view_menu = ViewMenu(self.level_view)

        self.menuBar().addMenu(self.view_menu)
        self.menuBar().addMenu(HelpMenu(self))

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
        splitter.setOrientation(Qt.Vertical)

        splitter.addWidget(self.object_list)
        splitter.setStretchFactor(0, 1)
        splitter.addWidget(self.jump_list)
        splitter.addWidget(jump_buttons)

        splitter.setChildrenCollapsible(False)

        self.level_toolbar = QToolBar("Level Info Toolbar", self)
        self.level_toolbar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.level_toolbar.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.level_toolbar.setOrientation(Qt.Horizontal)
        self.level_toolbar.setFloatable(False)

        self.level_toolbar.addWidget(self.spinner_panel)
        self.level_toolbar.addWidget(self.object_dropdown)
        self.level_toolbar.addWidget(size_and_palette)
        self.level_toolbar.addWidget(splitter)

        self.level_toolbar.setAllowedAreas(Qt.LeftToolBarArea | Qt.RightToolBarArea)

        self.addToolBar(Qt.RightToolBarArea, self.level_toolbar)

        self.object_toolbar = ObjectToolBar(self)
        self.object_toolbar.object_selected.connect(self._on_placeable_object_selected)

        object_toolbar = QToolBar("Object Toolbar", self)
        object_toolbar.setContextMenuPolicy(Qt.PreventContextMenu)
        object_toolbar.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        object_toolbar.setFloatable(False)

        object_toolbar.addWidget(self.object_toolbar)
        object_toolbar.setAllowedAreas(Qt.LeftToolBarArea | Qt.RightToolBarArea)

        self.addToolBar(Qt.LeftToolBarArea, object_toolbar)

        self.menu_toolbar = QToolBar("Menu Toolbar", self)
        self.menu_toolbar.setOrientation(Qt.Horizontal)
        self.menu_toolbar.setIconSize(TOOLBAR_ICON_SIZE)

        self.menu_toolbar.addAction(self.file_menu.settings_action)

        self.menu_toolbar.addSeparator()

        self.menu_toolbar.addAction(self.file_menu.open_rom_action)
        self.menu_toolbar.addAction(self.file_menu.save_rom_action)

        self.menu_toolbar.addSeparator()

        self.menu_toolbar.addAction(self.select_level_action)

        self.menu_toolbar.addSeparator()

        self.menu_toolbar.addAction(self.undo_action)
        self.menu_toolbar.addAction(self.redo_action)

        self.menu_toolbar.addSeparator()

        play_action = self.menu_toolbar.addAction(icon("play-circle.svg"), "Play Level")
        play_action.triggered.connect(self.on_play)
        play_action.setWhatsThis("Opens an emulator with the current Level set to 1-1.\nSee Settings.")

        self.menu_toolbar.addSeparator()

        self.menu_toolbar.addAction(icon("zoom-out.svg"), "Zoom Out").triggered.connect(self.level_view.zoom_out)
        self.menu_toolbar.addAction(icon("zoom-in.svg"), "Zoom In").triggered.connect(self.level_view.zoom_in)

        self.menu_toolbar.addSeparator()

        self.menu_toolbar.addAction(self.edit_header_action)
        self.edit_header_action.setWhatsThis(
            "<b>Header Editor</b><br/>"
            "Many configurations regarding the level are done in its header, like the length of "
            "the timer, or where and how Mario enters the level.<br/>"
        )

        self.jump_destination_action = self.menu_toolbar.addAction(
            icon("arrow-right-circle.svg"), "Go to Jump Destination"
        )
        self.jump_destination_action.triggered.connect(self._go_to_jump_destination)
        self.jump_destination_action.setWhatsThis(
            "Opens the level, that can be reached from this one, e.g. by entering a pipe."
        )

        self.menu_toolbar.addSeparator()

        whats_this_action = QWhatsThis.createAction()
        whats_this_action.setWhatsThis("Click on parts of the editor, to receive help information.")
        whats_this_action.setIcon(icon("help-circle.svg"))
        whats_this_action.setText("Starts 'What's this?' mode")
        self.menu_toolbar.addAction(whats_this_action)

        self.menu_toolbar.addSeparator()
        self.warning_list = WarningList(self, self.level_ref, self.level_view, self.object_list)

        warning_action = self.menu_toolbar.addAction(icon("alert-triangle.svg"), "Warning Panel")
        warning_action.setWhatsThis("Shows a list of warnings.")
        warning_action.triggered.connect(self.warning_list.show)
        warning_action.setDisabled(True)

        self.warning_list.warnings_updated.connect(warning_action.setEnabled)

        self.addToolBar(Qt.TopToolBarArea, self.menu_toolbar)

        self.status_bar = ObjectStatusBar(self, self.level_ref)
        self.setStatusBar(self.status_bar)

        self.delete_shortcut = QShortcut(QKeySequence(Qt.Key_Delete), self, self.remove_selected_objects)

        QShortcut(QKeySequence(Qt.CTRL | Qt.Key_X), self, self._cut_objects)
        QShortcut(QKeySequence(Qt.CTRL | Qt.Key_C), self, self._copy_objects)
        QShortcut(QKeySequence(Qt.CTRL | Qt.Key_V), self, self._paste_objects)

        self.undo_action.setShortcut(Qt.CTRL | Qt.Key_Z)
        self.redo_action.setShortcut(Qt.CTRL | Qt.SHIFT | Qt.Key_Z)

        QShortcut(QKeySequence(Qt.CTRL | Qt.Key_Plus), self, self.level_view.zoom_in)
        QShortcut(QKeySequence(Qt.CTRL | Qt.Key_Minus), self, self.level_view.zoom_out)

        QShortcut(QKeySequence(Qt.CTRL | Qt.Key_A), self, self.level_view.select_all)
        QShortcut(QKeySequence(Qt.CTRL | Qt.Key_L), self, self.object_dropdown.setFocus)

        self.check_for_update_on_startup()

        self.on_open_rom(path_to_rom)

        self.showMaximized()

    def _on_new_level(self, dont_check=False):
        if not dont_check and not self.safe_to_change():
            return

        object_set = ObjectSetSelector.get_object_set(self, alternative_title="Creating New Level")

        if object_set == -1:
            # was cancelled
            return

        ROM.reload_from_file()

        self.level_ref.level = Level(f"New {OBJECT_SET_NAMES[object_set]} Level", object_set_number=object_set)

        minimal_level_header = bytearray([0, 0, 0, 0, 0, 0, 0x81, object_set, 0])
        self.level_ref.level.from_bytes(object_data=(0, minimal_level_header), enemy_data=(0, bytearray()))

        self.level_ref.level_changed.emit()

    def _on_level_data_changed(self):
        level_is_not_attached = self.level_ref.level and not self.level_ref.level.attached_to_rom
        changes_were_made = not self.undo_stack.isClean() or PaletteGroup.changed

        self.file_menu.save_rom_action.setEnabled(level_is_not_attached or changes_were_made)

        self.jump_destination_action.setEnabled(bool(self.level_ref.level and self.level_ref.level.has_next_area))

        self._save_auto_data()

    def _on_show_settings(self):
        SettingsDialog(self.settings, self).exec()

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
        object_set = self.level_ref.level.next_area_object_set
        old_world = self.level_ref.level.world

        world, level = world_and_level_for_level_address(level_address + HEADER_LENGTH)

        ROM.reload_from_file()

        self.update_level(f"Level {world}-{level}", level_address, enemy_address, object_set)

        if world == -1:
            self.level_ref.level.world = old_world
        else:
            self.level_ref.level.world = world

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

        insta_player.skip_title_screen()

        save_all_palette_groups(temp_rom)

        temp_rom.save_to(path_to_temp_rom)

        return True

    def _show_jump_dest(self):
        header_editor = HeaderEditor(self, self.level_ref)
        header_editor.tab_widget.setCurrentIndex(3)

        header_editor.exec()

    def update_title(self):
        if self.level_view.level_ref is not None and ROM is not None:
            title = f"{self.level_view.level_ref.name} - {ROM.name}"
        else:
            title = "SMB3Foundry"

        self.setWindowTitle(title)

    def on_open_rom(self, path_to_rom=""):
        if not self.safe_to_change():
            return

        if not path_to_rom:
            # otherwise ask the user what new file to open
            path_to_rom, _ = QFileDialog.getOpenFileName(
                self,
                caption="Open ROM",
                dir=self.settings.value("editor/default dir path"),
                filter=ROM_FILE_FILTER,
            )

            if not path_to_rom:
                self._enable_disable_gui_elements()

                return

        # Proceed loading the file chosen by the user
        try:
            ROM.load_from_file(path_to_rom)

            self.close_level()

            self._ask_for_level_management()

            if path_to_rom == auto_save_rom_path:
                self._load_auto_save()
            else:
                self._save_auto_rom()
                if not self.open_level_selector(None):
                    self._on_new_level(dont_check=True)

        except IOError as exp:
            QMessageBox.warning(self, type(exp).__name__, f"Cannot open file '{path_to_rom}'.")
        finally:
            self._enable_disable_gui_elements()

    def on_open_m3l(self, _):
        if not self.safe_to_change():
            return

        # otherwise ask the user what new file to open
        if not (pathname := load_m3l_filename(self.settings.value("editor/default dir path"))):
            return

        ROM.reload_from_file()

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
        self.save_rom(False)

    def on_save_rom_as(self, _):
        self.save_rom(True)

    def _ask_for_level_management(self):
        if ROM.additional_data.managed_level_positions is not None:
            return

        answer = QMessageBox.question(
            self,
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

        ROM.additional_data.managed_level_positions = answer == QMessageBox.StandardButton.Yes

        if ROM.additional_data.managed_level_positions:
            pd = LevelParseProgressDialog()

            if pd.wasCanceled():
                ROM.additional_data.managed_level_positions = None
                return

            ROM.additional_data.found_levels = [
                pd.levels_by_address[key] for key in sorted(pd.levels_by_address.keys())
            ]

            lo = LevelOrganizer(ROM(), ROM().additional_data.found_levels)
            lo.rearrange_levels()
            lo.rearrange_enemies()

            ROM.save_to_file(ROM.path)

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
        elif answer == QMessageBox.RestoreDefaults:
            restore_all_palettes()
            self.level_ref.level.reload()

        return True

    def save_rom(self, is_save_as):
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
                dir=f"{self.settings.value('editor/default dir path')}/{suggested_file}",
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

        self._save_current_changes_to_file(pathname, set_new_path=True)

        self.update_title()

        if not is_save_as:
            self.undo_stack.setClean()

    def on_import_enemies_from_asm(self):
        if not (pathname := load_asm_filename("Enemy ASM", self.settings.value("editor/default dir path"))):
            return

        self.undo_stack.push(ImportASMEnemies(self.level_ref.level, pathname))

    def _attach_to_rom(self, object_data_offset: int, enemy_data_offset: int):
        if 0x0 in [object_data_offset, enemy_data_offset]:
            raise ValueError("You cannot save level or enemy data to the beginning of the ROM (address 0x0).")

        self.undo_stack.push(AttachLevelToRom(self.level_ref.level, object_data_offset, enemy_data_offset))

    def _save_current_changes_to_file(self, pathname: str, set_new_path: bool):
        super(FoundryMainWindow, self)._save_current_changes_to_file(pathname, set_new_path)

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

        ROM.reload_from_file()

        self.update_level(level_name, object_data, enemy_data, object_set)

        self.level_ref.level.world = world_index

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
        if self.sender() is self.object_toolbar:
            self.object_dropdown.select_object(level_object)
        else:
            self.object_toolbar.select_object(level_object)

    def bring_objects_to_foreground(self):
        self.undo_stack.push(ToForeground(self.level_ref.level, self.level_ref.selected_objects))

    def bring_objects_to_background(self):
        self.undo_stack.push(ToBackground(self.level_ref.level, self.level_ref.selected_objects))

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

    def _paste_objects(self, q_point: Optional[QPoint] = None):
        if not (copied_objects := self.context_menu.get_copied_objects())[0]:
            return

        copied_level_objects = cast(tuple[list[InLevelObject], Position], copied_objects)

        self.undo_stack.push(PasteObjectsAt(self.level_view, copied_level_objects, q_point))

    def remove_selected_objects(self):
        selected_objects = [obj for obj in self.level_ref.level.get_all_objects() if obj.selected]

        if not selected_objects:
            return

        self.undo_stack.push(RemoveObjects(self.level_ref.level, selected_objects))

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

            self.undo_stack.push(ReplaceLevelObject(self.level_ref.level, selected_object, domain, obj_type, length))
        else:
            self.undo_stack.push(ReplaceEnemy(self.level_ref.level, selected_object, obj_type))

        self.level_ref.data_changed.emit()

    def open_level_selector(self, _):
        if not self.safe_to_change():
            return

        level_selector = LevelSelector(self)
        if self.level_ref:
            level_selector.goto_world(self.level_ref.level.world)

        level_was_selected = level_selector.exec() == QDialog.Accepted

        if level_was_selected:
            ROM.reload_from_file()

            self.update_level(
                level_selector.level_name,
                level_selector.object_data_offset,
                level_selector.enemy_data_offset,
                level_selector.object_set,
            )

            self.level_ref.level.world = level_selector.world_index

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
    ):
        try:
            self.level_ref.load_level(level_name, object_data_offset, enemy_data_offset, object_set)
            self.scroll_panel.horizontalScrollBar().setValue(0)
            self.scroll_panel.verticalScrollBar().setValue(0)
        except IndexError:
            QMessageBox.critical(
                self,
                "Please confirm",
                "Failed loading level. The level offsets don't match.",
            )
            return

    def close_level(self):
        self.level_ref.level = None
        self.undo_stack.clear()
        self._enable_disable_gui_elements()

    def update_gui_for_level(self):
        restore_all_palettes()
        self.undo_stack.clear()

        self._enable_disable_gui_elements()

        self.update_title()
        self.jump_list.update()

        is_a_world_map = isinstance(self.level_ref.level, WorldMap)

        self.file_menu.save_m3l_action.setEnabled(not is_a_world_map)
        self.edit_header_action.setEnabled(not is_a_world_map)

        if is_a_world_map:
            self.object_dropdown.clear()
            self.object_dropdown.setEnabled(False)

            self.jump_list.setEnabled(False)
            self.jump_list.clear()
        else:
            self.object_dropdown.setEnabled(True)
            self.object_dropdown.set_object_set(self.level_ref.object_set_number, self.level_ref.graphic_set)

            self.jump_list.setEnabled(True)

        self.object_toolbar.set_object_set(self.level_ref.object_set_number, self.level_ref.graphic_set)

        self.level_view.update()

    def _enable_disable_gui_elements(self):
        # actions and widgets, that depend on whether the ROM is loaded
        rom_elements = [
            # entries in file menu
            self.file_menu.open_m3l_action,
            self.file_menu.open_level_asm_action,
            self.file_menu.save_rom_action,
            self.file_menu.save_rom_as_action,
            # entry in level menu
            self.select_level_action,
        ]

        # actions and widgets, that depend on whether a level is loaded or not
        level_elements = [
            # entry in file menu
            self.file_menu.save_m3l_action,
            self.file_menu.save_level_asm_action,
            self.file_menu.export_enemy_asm_action,
            # top toolbar
            self.menu_toolbar,
            # other gui elements
            self.level_view,
            self.level_toolbar,
            self.object_toolbar,
        ]

        level_elements.extend(self.level_menu.actions())
        level_elements.remove(self.undo_action)
        level_elements.remove(self.redo_action)
        level_elements.remove(self.select_level_action)
        level_elements.remove(self.new_level_action)

        level_elements.extend(self._rom_menu.actions())
        level_elements.extend(self.view_menu.actions())

        for gui_element in rom_elements:
            gui_element.setEnabled(ROM.is_loaded())

        for gui_element in level_elements:
            gui_element.setEnabled(ROM.is_loaded() and self.level_ref.fully_loaded)

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
        self.undo_stack.push(AddJump(self.level_ref.level))

    def on_jump_removed(self):
        self.undo_stack.push(RemoveJump(self.level_ref.level, self.jump_list.currentIndex().row()))

    def on_jump_edited(self, jump: Jump):
        index = self.jump_list.currentIndex().row()

        assert index >= 0

        if not isinstance(self.level_ref.level, Level):
            return

        old_jump = self.level_ref.level.jumps[index]

        self.undo_stack.beginMacro(f"Editing {old_jump}")

        self.undo_stack.push(RemoveJump(self.level_ref.level, index))
        self.undo_stack.push(AddJump(self.level_ref.level, jump, index))

        self.jump_list.item(index).setText(str(jump))

        self.undo_stack.endMacro()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MiddleButton:
            pos = self.level_view.mapFromGlobal(self.mapToGlobal(event.position().toPoint()))

            self.place_object_from_dropdown(pos)

    def place_object_from_dropdown(self, q_point: QPoint) -> None:
        # the dropdown is synchronized with the toolbar, so it doesn't matter where to take it from
        in_level_object = self.object_dropdown.currentData(Qt.UserRole)

        self.object_toolbar.add_recent_object(in_level_object)

        if isinstance(in_level_object, LevelObject):
            self.add_object_at(q_point, in_level_object.domain, in_level_object.obj_index)
        elif isinstance(in_level_object, EnemyItem):
            self.add_enemy_at(q_point, in_level_object.obj_index)

        self.level_ref.level.data_changed.emit()

    def closeEvent(self, event: QCloseEvent):
        super(FoundryMainWindow, self).closeEvent(event)

        auto_save_rom_path.unlink(missing_ok=True)
        auto_save_m3l_path.unlink(missing_ok=True)
        auto_save_level_data_path.unlink(missing_ok=True)
