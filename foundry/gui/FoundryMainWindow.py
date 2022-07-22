import base64
import json
import logging
import os
import pathlib
import shlex
import subprocess
import tempfile
from typing import Optional

from PySide6.QtCore import QPoint, QSize
from PySide6.QtGui import QAction, QCloseEvent, QKeySequence, QMouseEvent, QShortcut, QUndoStack, Qt
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
    M3L_FILE_FILTER,
    ROM_FILE_FILTER,
    auto_save_level_data_path,
    auto_save_m3l_path,
    auto_save_rom_path,
    icon,
)
from foundry.game.File import ROM
from foundry.game.ObjectSet import OBJECT_SET_NAMES
from foundry.game.gfx.Palette import PaletteGroup, restore_all_palettes, save_all_palette_groups
from foundry.game.gfx.objects import EnemyItem, Jump, LevelObject
from foundry.game.gfx.objects.in_level.in_level_object import InLevelObject
from foundry.game.level.Level import Level, world_and_level_for_level_address
from foundry.game.level.WorldMap import WorldMap
from foundry.gui.AutoScrollEditor import AutoScrollEditor
from foundry.gui.ContextMenu import CMAction, ID_PROP, LevelContextMenu
from foundry.gui.EnemySizeBar import EnemySizeBar
from foundry.gui.HeaderEditor import HeaderEditor
from foundry.gui.JumpEditor import JumpEditor
from foundry.gui.JumpList import JumpList
from foundry.gui.LevelSelector import LevelSelector
from foundry.gui.LevelSizeBar import LevelSizeBar
from foundry.gui.LevelView import LevelView
from foundry.gui.MainWindow import MainWindow
from foundry.gui.ObjectDropdown import ObjectDropdown
from foundry.gui.ObjectList import ObjectList
from foundry.gui.ObjectSetSelector import ObjectSetSelector
from foundry.gui.ObjectStatusBar import ObjectStatusBar
from foundry.gui.ObjectToolBar import ObjectToolBar
from foundry.gui.PaletteViewer import SidePalette
from foundry.gui.SettingsDialog import POWERUPS, SettingsDialog
from foundry.gui.SpinnerPanel import SpinnerPanel
from foundry.gui.WarningList import WarningList
from foundry.gui.commands import (
    AddEnemyAt,
    AddJump,
    AddLevelObjectAt,
    AttachLevelToRom,
    PasteObjectsAt,
    RemoveJump,
    RemoveObjects,
    ReplaceEnemy,
    ReplaceLevelObject,
    ToBackground,
    ToForeground,
)
from foundry.gui.menus.help_menu import HelpMenu
from foundry.gui.menus.object_menu import ObjectMenu
from foundry.gui.menus.view_menu import ViewMenu
from foundry.gui.settings import Settings
from smb3parse.constants import TILE_LEVEL_1, Title_DebugMenu, Title_PrepForWorldMap
from smb3parse.levels.world_map import WorldMap as SMB3World
from smb3parse.util.rom import Rom as SMB3Rom


class FoundryMainWindow(MainWindow):
    def __init__(self, path_to_rom=""):
        super(FoundryMainWindow, self).__init__()

        self.settings = Settings("mchlnix", "foundry")

        self.setWindowIcon(icon("foundry.ico"))
        self.setStyleSheet(self.settings.value("editor/gui_style"))

        self.undo_stack = QUndoStack(self)
        self.undo_stack.setObjectName("undo_stack")

        file_menu = QMenu("&File")

        open_rom_action = file_menu.addAction("Open ROM")
        open_rom_action.setIcon(icon("folder.svg"))
        open_rom_action.triggered.connect(self.on_open_rom)

        self.open_m3l_action = file_menu.addAction("Open M3L")
        self.open_m3l_action.setIcon(icon("folder.svg"))
        self.open_m3l_action.triggered.connect(self.on_open_m3l)

        file_menu.addSeparator()

        self.save_rom_action = file_menu.addAction("Save ROM")
        self.save_rom_action.triggered.connect(self.on_save_rom)
        self.save_rom_action.setIcon(icon("save.svg"))

        self.save_rom_as_action = file_menu.addAction("Save ROM as ...")
        self.save_rom_as_action.triggered.connect(self.on_save_rom_as)
        self.save_rom_as_action.setIcon(icon("save.svg"))

        self.save_m3l_action = file_menu.addAction("Save M3L")
        self.save_m3l_action.setIcon(icon("file-text.svg"))
        self.save_m3l_action.triggered.connect(self.on_save_m3l)

        file_menu.addSeparator()

        settings_action = file_menu.addAction("Editor Settings")
        settings_action.setIcon(icon("sliders.svg"))
        settings_action.triggered.connect(self._on_show_settings)

        file_menu.addSeparator()

        exit_action = file_menu.addAction("Exit")
        exit_action.setIcon(icon("power.svg"))
        exit_action.triggered.connect(lambda _: self.close())

        self.menuBar().addMenu(file_menu)

        self.level_menu = QMenu("&Level")

        self.undo_action = self.undo_stack.createUndoAction(self)
        self.undo_action.setIcon(icon("rotate-ccw.svg"))
        self.level_menu.addAction(self.undo_action)

        self.redo_action = self.undo_stack.createRedoAction(self)
        self.redo_action.setIcon(icon("rotate-cw.svg"))
        self.level_menu.addAction(self.redo_action)

        self.select_level_action = self.level_menu.addAction("Select Level")
        self.select_level_action.setIcon(icon("globe.svg"))
        self.select_level_action.triggered.connect(self.open_level_selector)

        self.reload_action = self.level_menu.addAction("Reload Level")
        self.reload_action.setIcon(icon("refresh-cw.svg"))
        self.reload_action.triggered.connect(self.reload_level)

        self.level_menu.addSeparator()

        self.new_level_action = self.level_menu.addAction("New Empty Level")
        self.new_level_action.setIcon(icon("file.svg"))
        self.new_level_action.triggered.connect(self._on_new_level)

        self.level_menu.addSeparator()

        self.edit_header_action = self.level_menu.addAction("Edit Level Header")
        self.edit_header_action.setIcon(icon("tool.svg"))
        self.edit_header_action.triggered.connect(self.on_header_editor)

        self.edit_autoscroll = self.level_menu.addAction("Edit Autoscrolling")
        self.edit_autoscroll.setIcon(icon("fast-forward.svg"))
        self.edit_autoscroll.triggered.connect(self.on_edit_autoscroll)

        self.menuBar().addMenu(self.level_menu)

        self._object_menu = ObjectMenu(self.level_ref)
        self.menuBar().addMenu(self._object_menu)

        self.context_menu = LevelContextMenu(self.level_ref)
        self.context_menu.triggered.connect(self.on_menu)

        self.level_view = LevelView(self, self.level_ref, self.settings, self.context_menu)

        self.view_menu = ViewMenu(self.level_view)

        self.menuBar().addMenu(self.view_menu)
        self.menuBar().addMenu(HelpMenu(self))

        self.undo_stack.indexChanged.connect(self._on_level_data_changed)

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

        level_toolbar = QToolBar("Level Info Toolbar", self)
        level_toolbar.setContextMenuPolicy(Qt.PreventContextMenu)
        level_toolbar.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        level_toolbar.setOrientation(Qt.Horizontal)
        level_toolbar.setFloatable(False)

        level_toolbar.addWidget(self.spinner_panel)
        level_toolbar.addWidget(self.object_dropdown)
        level_toolbar.addWidget(size_and_palette)
        level_toolbar.addWidget(splitter)

        level_toolbar.setAllowedAreas(Qt.LeftToolBarArea | Qt.RightToolBarArea)

        self.addToolBar(Qt.RightToolBarArea, level_toolbar)

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
        self.menu_toolbar.setIconSize(QSize(20, 20))

        self.menu_toolbar.addAction(settings_action)
        self.menu_toolbar.addSeparator()
        self.menu_toolbar.addAction(open_rom_action)
        self.menu_toolbar.addAction(self.save_rom_action)

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

        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_X), self, self._cut_objects)
        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_C), self, self._copy_objects)
        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_V), self, self._paste_objects)

        self.undo_action.setShortcut(Qt.CTRL + Qt.Key_Z)
        self.redo_action.setShortcut(Qt.CTRL + Qt.SHIFT + Qt.Key_Z)

        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_Plus), self, self.level_view.zoom_in)
        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_Minus), self, self.level_view.zoom_out)

        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_A), self, self.level_view.select_all)
        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_L), self, self.object_dropdown.setFocus)

        self.on_open_rom(path_to_rom)

        self.showMaximized()

    def _on_new_level(self, dont_check=False):
        if not dont_check and not self.safe_to_change():
            return

        object_set = ObjectSetSelector.get_object_set(self)

        if object_set == -1:
            # was cancelled
            return

        self.level_ref.level = Level(f"New {OBJECT_SET_NAMES[object_set]} Level", object_set_number=object_set)

        minimal_level_header = bytearray([0, 0, 0, 0, 0, 0, 0x81, object_set, 0])
        self.level_ref.level.from_bytes(object_data=(0, minimal_level_header), enemy_data=(0, bytearray()))

        self.update_gui_for_level()

    def _on_level_data_changed(self):
        self.save_rom_action.setEnabled(not self.undo_stack.isClean() or PaletteGroup.changed)

        self.jump_destination_action.setEnabled(bool(self.level_ref.level and self.level_ref.level.has_next_area))

        self._save_auto_data()

    def _on_show_settings(self):
        SettingsDialog(self, self.settings).exec()

    @staticmethod
    def _save_auto_rom():
        ROM().save_to_file(auto_save_rom_path, set_new_path=False)

    def _save_auto_data(self):
        if not self.level_ref:
            return

        (object_offset, object_bytes), (enemy_offset, enemy_bytes) = self.level_ref.level.to_bytes()

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

        with open(auto_save_level_data_path, "w") as level_data_file:
            level_data_file.write(json.dumps(data_dict))

    def _load_auto_save(self):
        # rom already loaded
        with open(auto_save_level_data_path, "r") as level_data_file:
            json_data = level_data_file.read()

            data_dict = json.loads(json_data)

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

            with open(auto_save_m3l_path, "rb") as m3l_file:
                self.load_m3l(bytearray(m3l_file.read()), auto_save_m3l_path)
        else:
            self.update_level("recovered level", object_address, enemy_address, object_set_number)
            self.level_ref.level.from_bytes((object_address, object_data), (enemy_address, enemy_data), True)

    def _go_to_jump_destination(self):
        if not self.safe_to_change():
            return

        level_address = self.level_ref.level.next_area_objects
        enemy_address = self.level_ref.level.next_area_enemies + 1
        object_set = self.level_ref.level.next_area_object_set

        world, level = world_and_level_for_level_address(level_address)

        self.update_level(f"Level {world}-{level}", level_address, enemy_address, object_set)

    def on_play(self):
        """
        Copies the ROM, including the current level, to a temporary directory, saves the current level as level 1-1 and
        opens the rom in an emulator.
        """
        temp_dir = pathlib.Path(tempfile.gettempdir()) / "smb3foundry"
        temp_dir.mkdir(parents=True, exist_ok=True)

        path_to_temp_rom = temp_dir / "instaplay.rom"

        ROM().save_to(path_to_temp_rom)

        temp_rom = self._open_rom(path_to_temp_rom)

        if not self._put_current_level_to_level_1_1(temp_rom):
            return

        if not self._set_default_powerup(temp_rom):
            return

        save_all_palette_groups(temp_rom)

        temp_rom.save_to(path_to_temp_rom)

        arguments = self.settings.value("editor/instaplay_arguments").replace("%f", str(path_to_temp_rom))
        arguments = shlex.split(arguments, posix=False)

        emu_path = pathlib.Path(self.settings.value("editor/instaplay_emulator"))

        if emu_path.is_absolute():
            if emu_path.exists():
                emulator = str(emu_path)
            else:
                QMessageBox.critical(
                    self, "Emulator not found", f"Check it under File > Settings.\nFile {emu_path} not found."
                )
                return
        else:
            emulator = self.settings.value("editor/instaplay_emulator")

        try:
            subprocess.run([emulator, *arguments])
        except Exception as e:
            QMessageBox.critical(self, "Emulator command failed.", f"Check it under File > Settings.\n{str(e)}")

    @staticmethod
    def _open_rom(path_to_rom):
        with open(path_to_rom, "rb") as smb3_rom:
            data = smb3_rom.read()

        rom = SMB3Rom(bytearray(data))
        return rom

    def _show_jump_dest(self):
        header_editor = HeaderEditor(self, self.level_ref)
        header_editor.tab_widget.setCurrentIndex(3)

        header_editor.exec()

    def _put_current_level_to_level_1_1(self, rom: SMB3Rom) -> bool:
        # load world-1 data
        world_1 = SMB3World.from_world_number(rom, 1)

        # find position of "level 1" tile in world map
        for position in world_1.gen_positions():
            if position.tile() == TILE_LEVEL_1:
                break
        else:
            QMessageBox.critical(
                self, "Couldn't place level", "Could not find a level 1 tile in World 1 to put your level at."
            )
            return False

        if not self.level_ref.level.attached_to_rom:
            QMessageBox.critical(
                self,
                "Couldn't place level",
                "The Level is not part of the rom yet (M3L?). Try saving it into the ROM first.",
            )
            return False

        # write level and enemy data of current level
        (layout_address, layout_bytes), (enemy_address, enemy_bytes) = self.level_ref.level.to_bytes()
        rom.write(layout_address, layout_bytes)
        rom.write(enemy_address, enemy_bytes)

        # replace level information with that of current level
        object_set_number = self.level_ref.object_set_number

        world_1.replace_level_at_position((layout_address, enemy_address - 1, object_set_number), position)

        return True

    def _set_default_powerup(self, rom: SMB3Rom) -> bool:
        assert isinstance(self.settings.value("editor/default_powerup"), int)

        *_, powerup, hasPWing = POWERUPS[self.settings.value("editor/default_powerup")]

        rom.write(Title_PrepForWorldMap + 0x1, bytes([powerup]))

        nop = 0xEA
        rts = 0x60
        lda = 0xA9
        staAbsolute = 0x8D

        # If a P-wing powerup is selected, another variable needs to be set with the P-wing value
        # This piece of code overwrites a part of Title_DebugMenu
        if hasPWing:
            Map_Power_DispHigh = 0x03
            Map_Power_DispLow = 0xF3

            # We need to start one byte before Title_DebugMenu to remove the RTS of Title_PrepForWorldMap
            # The assembly code below reads as follows:
            # LDA 0x08
            # STA $03F3
            # RTS
            rom.write(
                Title_DebugMenu - 0x1,
                bytes(
                    [
                        lda,
                        0x8,
                        staAbsolute,
                        Map_Power_DispLow,
                        Map_Power_DispHigh,
                        # The RTS to get out of the now extended Title_PrepForWorldMap
                        rts,
                    ]
                ),
            )

            # Remove code that resets the powerup value by replacing it with no-operations
            # Otherwise this code would copy the value of the normal powerup here
            # (So if the powerup would be Raccoon Mario, Map_Power_Disp would also be
            # set as Raccoon Mario instead of P-wing
            Map_Power_DispResetLocation = 0x3C5A2
            rom.write(Map_Power_DispResetLocation, bytes([nop, nop, nop]))

        return True

    def update_title(self):
        if self.level_view.level_ref is not None and ROM is not None:
            title = f"{self.level_view.level_ref.name} - {ROM.name}"
        else:
            title = "SMB3Foundry"

        self.setWindowTitle(title)

    def on_open_rom(self, path_to_rom="") -> bool:
        if not self.safe_to_change():
            return False

        if not path_to_rom:
            # otherwise ask the user what new file to open
            path_to_rom, _ = QFileDialog.getOpenFileName(self, caption="Open ROM", filter=ROM_FILE_FILTER)

            if not path_to_rom:
                self._enable_disable_gui_elements()

        # Proceed loading the file chosen by the user
        try:
            ROM.load_from_file(path_to_rom)

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

    def on_open_m3l(self, _) -> bool:
        if not self.safe_to_change():
            return False

        # otherwise ask the user what new file to open
        pathname, _ = QFileDialog.getOpenFileName(self, caption="Open M3L file", filter=M3L_FILE_FILTER)

        if not pathname:
            return False

        # Proceed loading the file chosen by the user
        try:
            with open(pathname, "rb") as m3l_file:

                m3l_data = bytearray(m3l_file.read())
        except IOError as exp:
            QMessageBox.warning(self, type(exp).__name__, f"Cannot open file '{pathname}'.")

            return False

        self.load_m3l(m3l_data, pathname)
        self.save_m3l(auto_save_m3l_path, self.level_ref.level.to_m3l())

        return True

    def load_m3l(self, m3l_data: bytearray, pathname: str):
        if not self._ask_for_palette_save():
            return

        if self.level_ref.level is None:
            self.level_ref.level = Level()

        self.level_ref.level.from_m3l(m3l_data)

        self.level_view.level_ref.name = os.path.basename(pathname)

        self.update_gui_for_level()

    def safe_to_change(self) -> bool:
        return super(FoundryMainWindow, self).safe_to_change() and self._ask_for_palette_save()

    def on_save_rom(self, _):
        self.save_rom(False)

    def on_save_rom_as(self, _):
        self.save_rom(True)

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
            "you want to save these changes?",
            QMessageBox.Cancel | QMessageBox.RestoreDefaults | QMessageBox.Yes,
            QMessageBox.Cancel,
        )

        if answer == QMessageBox.Cancel:
            return False

        if answer == QMessageBox.Yes:
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

        if not self.level_ref.attached_to_rom:
            QMessageBox.information(
                self,
                "Importing M3L into ROM",
                "You are currently editing a level stored in an m3l file outside of the ROM. Please select the "
                "positions in the ROM you want the level objects and enemies/items to be stored.",
                QMessageBox.Ok,
            )

            level_selector = LevelSelector(self)

            answer = level_selector.exec()

            if answer != QMessageBox.Accepted:
                return

            if level_selector.object_set != self.level_ref.level.object_set.number:
                QMessageBox.critical(
                    self,
                    "Couldn't save M3L file into ROM.",
                    "You selected a level, that has a different object set "
                    f"({OBJECT_SET_NAMES[level_selector.object_set]}), than the level you are trying to save "
                    f"into the ROM ({OBJECT_SET_NAMES[self.level_ref.level.object_set.number]}). This is currently "
                    "not supported. Please find a level, that has the same object set.",
                )
                return

            if not self._ask_for_palette_save():
                return

            self._attach_to_rom(level_selector.object_data_offset, level_selector.enemy_data_offset)

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
                self, caption="Save ROM as", dir=suggested_file, filter=ROM_FILE_FILTER
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

    def _attach_to_rom(self, object_data_offset: int, enemy_data_offset: int):
        if 0x0 in [object_data_offset, enemy_data_offset]:
            raise ValueError("You cannot save level or enemy data to the beginning of the ROM (address 0x0).")

        self.undo_stack.push(AttachLevelToRom(self.level_ref.level, object_data_offset, enemy_data_offset))

    def _save_current_changes_to_file(self, pathname: str, set_new_path: bool):
        super(FoundryMainWindow, self)._save_current_changes_to_file(pathname, set_new_path)

        self._save_auto_rom()

    def on_save_m3l(self, _):
        suggested_file = self.level_view.level_ref.name

        if not suggested_file.endswith(".m3l"):
            suggested_file += ".m3l"

        pathname, _ = QFileDialog.getSaveFileName(
            self, caption="Save M3L as", dir=suggested_file, filter=M3L_FILE_FILTER
        )

        if not pathname:
            return

        m3l_bytes = self.level_view.level_ref.level.to_m3l()

        self.save_m3l(pathname, m3l_bytes)

    def save_m3l(self, pathname: os.PathLike, m3l_bytes: bytearray):
        try:
            with open(pathname, "wb") as m3l_file:
                m3l_file.write(m3l_bytes)
        except IOError as exp:
            QMessageBox.warning(self, type(exp).__name__, f"Couldn't save level to '{pathname}'.")

    def on_menu(self, action: QAction):
        item_id = action.property(ID_PROP)

        if item_id in self.context_menu.get_all_menu_item_ids():
            if item_id == CMAction.REMOVE:
                self.remove_selected_objects()
            elif item_id == CMAction.ADD_OBJECT:
                selected_object = self.object_dropdown.currentIndex()

                if selected_object != -1:
                    self.place_object_from_dropdown(self.context_menu.get_position())
                else:
                    self.add_object_at(self.context_menu.get_position())

            elif item_id == CMAction.CUT:
                self._cut_objects()
            elif item_id == CMAction.COPY:
                self._copy_objects()
            elif item_id == CMAction.PASTE:
                self._paste_objects(self.context_menu.get_position())
            elif item_id == CMAction.FOREGROUND:
                self.bring_objects_to_foreground()
            elif item_id == CMAction.BACKGROUND:
                self.bring_objects_to_background()

        self.level_view.update()

    def reload_level(self):
        if not self.safe_to_change():
            return

        level_name = self.level_view.level_ref.name
        object_data = self.level_view.level_ref.header_offset
        enemy_data = self.level_view.level_ref.enemy_offset
        object_set = self.level_view.level_ref.object_set_number

        self.update_level(level_name, object_data, enemy_data, object_set)

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

        self.undo_stack.push(PasteObjectsAt(self.level_view, copied_objects, q_point))

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

        level_was_selected = level_selector.exec() == QDialog.Accepted

        if level_was_selected:
            self.update_level(
                level_selector.level_name,
                level_selector.object_data_offset,
                level_selector.enemy_data_offset,
                level_selector.object_set,
            )

        return level_was_selected

    def on_edit_autoscroll(self, _):
        AutoScrollEditor(self, self.level_ref).exec()

    def on_header_editor(self, _):
        HeaderEditor(self, self.level_ref).exec()

    def update_level(self, level_name: str, object_data_offset: int, enemy_data_offset: int, object_set: int):
        try:
            self.level_ref.load_level(level_name, object_data_offset, enemy_data_offset, object_set)
        except IndexError:
            QMessageBox.critical(self, "Please confirm", "Failed loading level. The level offsets don't match.")
            return

        self.update_gui_for_level()

    def update_gui_for_level(self):
        restore_all_palettes()
        self.undo_stack.clear()

        self._enable_disable_gui_elements()

        self.update_title()
        self.jump_list.update()

        is_a_world_map = isinstance(self.level_ref.level, WorldMap)

        self.save_m3l_action.setEnabled(not is_a_world_map)
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
            self.open_m3l_action,
            self.save_rom_action,
            self.save_rom_as_action,
            # entry in level menu
            self.select_level_action,
        ]

        # actions and widgets, that depend on whether a level is loaded or not
        level_elements = [
            # entry in file menu
            self.save_m3l_action,
            # top toolbar
            self.menu_toolbar,
            # other gui elements
            self.level_view,
            self.spinner_panel,
            self.object_toolbar,
            self.level_size_bar,
            self.enemy_size_bar,
            self.object_list,
            self.jump_list,
            self.object_toolbar,
        ]

        level_elements.extend(self.level_menu.actions())
        level_elements.remove(self.level_menu.actions()[0])
        level_elements.remove(self.level_menu.actions()[1])
        level_elements.remove(self.select_level_action)
        level_elements.remove(self.new_level_action)

        level_elements.extend(self._object_menu.actions())
        level_elements.extend(self.view_menu.actions())

        for gui_element in rom_elements:
            gui_element.setEnabled(ROM.is_loaded())

        for gui_element in level_elements:
            gui_element.setEnabled(ROM.is_loaded() and self.level_ref.fully_loaded)

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
            pos = self.level_view.mapFromGlobal(self.mapToGlobal(event.pos()))

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
