import base64
import json
import logging
import os
import pathlib
import shlex
import subprocess
import tempfile
from typing import Tuple, Union

from PySide2.QtCore import QSize
from PySide2.QtGui import QCloseEvent, QKeySequence, QMouseEvent, Qt
from PySide2.QtWidgets import (
    QAction,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QShortcut,
    QSizePolicy,
    QSplitter,
    QToolBar,
    QVBoxLayout,
    QWhatsThis,
    QWidget,
)

from foundry import (
    auto_save_level_data_path,
    auto_save_m3l_path,
    auto_save_rom_path,
    discord_link,
    enemy_compat_link,
    feature_video_link,
    get_current_version_name,
    get_latest_version_name,
    github_link,
    icon,
    open_url,
    releases_link,
)
from foundry.game.File import ROM
from foundry.game.ObjectSet import OBJECT_SET_NAMES
from foundry.game.gfx.Palette import PaletteGroup, restore_all_palettes, save_all_palette_groups
from foundry.game.gfx.objects.EnemyItem import EnemyObject
from foundry.game.gfx.objects.LevelObject import LevelObject
from foundry.game.level.Level import Level, world_and_level_for_level_address
from foundry.game.level.LevelRef import LevelRef
from foundry.game.level.WorldMap import WorldMap
from foundry.gui.AboutWindow import AboutDialog
from foundry.gui.AutoScrollEditor import AutoScrollEditor
from foundry.gui.BlockViewer import BlockViewer
from foundry.gui.ContextMenu import CMAction, ContextMenu
from foundry.gui.EnemySizeBar import EnemySizeBar
from foundry.gui.HeaderEditor import HeaderEditor
from foundry.gui.JumpEditor import JumpEditor
from foundry.gui.JumpList import JumpList
from foundry.gui.LevelSelector import LevelSelector
from foundry.gui.LevelSizeBar import LevelSizeBar
from foundry.gui.LevelView import LevelView, undoable
from foundry.gui.ObjectDropdown import ObjectDropdown
from foundry.gui.ObjectList import ObjectList
from foundry.gui.ObjectSetSelector import ObjectSetSelector
from foundry.gui.ObjectStatusBar import ObjectStatusBar
from foundry.gui.ObjectToolBar import ObjectToolBar
from foundry.gui.ObjectViewer import ObjectViewer
from foundry.gui.PaletteViewer import PaletteViewer, SidePalette
from foundry.gui.SettingsDialog import POWERUPS, SettingsDialog
from foundry.gui.SpinnerPanel import SpinnerPanel
from foundry.gui.WarningList import WarningList
from foundry.gui.settings import SETTINGS, save_settings
from smb3parse.constants import TILE_LEVEL_1, Title_DebugMenu, Title_PrepForWorldMap
from smb3parse.levels.world_map import WorldMap as SMB3World
from smb3parse.util.rom import Rom as SMB3Rom

ROM_FILE_FILTER = "ROM files (*.nes *.rom);;All files (*)"
M3L_FILE_FILTER = "M3L files (*.m3l);;All files (*)"
IMG_FILE_FILTER = "Screenshots (*.png);;All files (*)"

ID_RELOAD_LEVEL = 303

ID_GRID_LINES = 501
ID_TRANSPARENCY = 508
ID_JUMPS = 509
ID_MARIO = 510
ID_RESIZE_TYPE = 511
ID_JUMP_OBJECTS = 512
ID_ITEM_BLOCKS = 513
ID_INVISIBLE_ITEMS = 514
ID_AUTOSCROLL = 515

CHECKABLE_MENU_ITEMS = [
    ID_TRANSPARENCY,
    ID_GRID_LINES,
    ID_JUMPS,
    ID_MARIO,
    ID_RESIZE_TYPE,
    ID_JUMP_OBJECTS,
    ID_ITEM_BLOCKS,
    ID_INVISIBLE_ITEMS,
    ID_AUTOSCROLL,
]

ID_PROP = "ID"

# mouse modes

MODE_FREE = 0
MODE_DRAG = 1
MODE_RESIZE = 2


class MainWindow(QMainWindow):
    def __init__(self, path_to_rom=""):
        super(MainWindow, self).__init__()

        self.setWindowIcon(icon("foundry.ico"))
        self.setStyleSheet(SETTINGS["gui_style"])

        file_menu = QMenu("File")

        open_rom_action = file_menu.addAction("&Open ROM")
        open_rom_action.triggered.connect(self.on_open_rom)
        self.open_m3l_action = file_menu.addAction("&Open M3L")
        self.open_m3l_action.triggered.connect(self.on_open_m3l)

        file_menu.addSeparator()

        self.save_rom_action = file_menu.addAction("&Save ROM")
        self.save_rom_action.triggered.connect(self.on_save_rom)
        self.save_rom_as_action = file_menu.addAction("&Save ROM as ...")
        self.save_rom_as_action.triggered.connect(self.on_save_rom_as)
        """
        file_menu.AppendSeparator()
        """
        self.save_m3l_action = file_menu.addAction("&Save M3L")
        self.save_m3l_action.triggered.connect(self.on_save_m3l)
        """
        file_menu.Append(ID_SAVE_LEVEL_TO, "&Save Level to", "")
        file_menu.AppendSeparator()
        file_menu.Append(ID_APPLY_IPS_PATCH, "&Apply IPS Patch", "")
        file_menu.AppendSeparator()
        file_menu.Append(ID_ROM_PRESET, "&ROM Preset", "")
        """
        file_menu.addSeparator()
        settings_action = file_menu.addAction("&Settings")
        settings_action.triggered.connect(self._on_show_settings)
        file_menu.addSeparator()
        exit_action = file_menu.addAction("&Exit")
        exit_action.triggered.connect(lambda _: self.close())

        self.menuBar().addMenu(file_menu)

        """
        edit_menu = wx.Menu()

        edit_menu.Append(ID_EDIT_LEVEL, "&Edit Level", "")
        edit_menu.Append(ID_EDIT_OBJ_DEFS, "&Edit Object Definitions", "")
        edit_menu.Append(ID_EDIT_PALETTE, "&Edit Palette", "")
        edit_menu.Append(ID_EDIT_GRAPHICS, "&Edit Graphics", "")
        edit_menu.Append(ID_EDIT_MISC, "&Edit Miscellaneous", "")
        edit_menu.AppendSeparator()
        edit_menu.Append(ID_FREE_FORM_MODE, "&Free form Mode", "")
        edit_menu.Append(ID_LIMIT_SIZE, "&Limit Size", "")
        """

        self.level_menu = QMenu("Level")

        self.select_level_action = self.level_menu.addAction("&Select Level")
        self.select_level_action.triggered.connect(self.open_level_selector)

        self.reload_action = self.level_menu.addAction("&Reload Level")
        self.reload_action.triggered.connect(self.reload_level)
        self.level_menu.addSeparator()
        self.new_level_action = self.level_menu.addAction("New Empty Level")
        self.new_level_action.triggered.connect(self._on_new_level)
        self.level_menu.addSeparator()
        self.edit_header_action = self.level_menu.addAction("&Edit Level Header")
        self.edit_header_action.triggered.connect(self.on_header_editor)
        self.edit_autoscroll = self.level_menu.addAction("Edit Autoscrolling")
        self.edit_autoscroll.triggered.connect(self.on_edit_autoscroll)

        self.menuBar().addMenu(self.level_menu)

        self.object_menu = QMenu("Objects")

        view_blocks_action = self.object_menu.addAction("&View Blocks")
        view_blocks_action.triggered.connect(self.on_block_viewer)
        view_objects_action = self.object_menu.addAction("&View Objects")
        view_objects_action.triggered.connect(self.on_object_viewer)
        self.object_menu.addSeparator()
        view_palettes_action = self.object_menu.addAction("View Object Palettes")
        view_palettes_action.triggered.connect(self.on_palette_viewer)

        self.menuBar().addMenu(self.object_menu)

        self.view_menu = QMenu("View")
        self.view_menu.triggered.connect(self.on_menu)

        action = self.view_menu.addAction("Mario")
        action.setProperty(ID_PROP, ID_MARIO)
        action.setCheckable(True)
        action.setChecked(SETTINGS["draw_mario"])

        action = self.view_menu.addAction("&Jumps on objects")
        action.setProperty(ID_PROP, ID_JUMP_OBJECTS)
        action.setCheckable(True)
        action.setChecked(SETTINGS["draw_jump_on_objects"])

        action = self.view_menu.addAction("Items in blocks")
        action.setProperty(ID_PROP, ID_ITEM_BLOCKS)
        action.setCheckable(True)
        action.setChecked(SETTINGS["draw_items_in_blocks"])

        action = self.view_menu.addAction("Invisible items")
        action.setProperty(ID_PROP, ID_INVISIBLE_ITEMS)
        action.setCheckable(True)
        action.setChecked(SETTINGS["draw_invisible_items"])

        action = self.view_menu.addAction("Autoscroll Path")
        action.setProperty(ID_PROP, ID_AUTOSCROLL)
        action.setCheckable(True)
        action.setChecked(SETTINGS["draw_autoscroll"])

        self.view_menu.addSeparator()

        action = self.view_menu.addAction("Jump Zones")
        action.setProperty(ID_PROP, ID_JUMPS)
        action.setCheckable(True)
        action.setChecked(SETTINGS["draw_jumps"])

        action = self.view_menu.addAction("&Grid lines")
        action.setProperty(ID_PROP, ID_GRID_LINES)
        action.setCheckable(True)
        action.setChecked(SETTINGS["draw_grid"])

        action = self.view_menu.addAction("Resize Type")
        action.setProperty(ID_PROP, ID_RESIZE_TYPE)
        action.setCheckable(True)
        action.setChecked(SETTINGS["draw_expansion"])

        self.view_menu.addSeparator()

        action = self.view_menu.addAction("&Block Transparency")
        action.setProperty(ID_PROP, ID_TRANSPARENCY)
        action.setCheckable(True)
        action.setChecked(SETTINGS["block_transparency"])

        self.view_menu.addSeparator()
        self.view_menu.addAction("&Save Screenshot of Level").triggered.connect(self.on_screenshot)
        """
        self.view_menu.Append(ID_BACKGROUND_FLOOR, "&Background & Floor", "")
        self.view_menu.Append(ID_TOOLBAR, "&Toolbar", "")
        self.view_menu.AppendSeparator()
        self.view_menu.Append(ID_ZOOM, "&Zoom", "")
        self.view_menu.AppendSeparator()
        self.view_menu.Append(ID_USE_ROM_GRAPHICS, "&Use ROM Graphics", "")
        self.view_menu.Append(ID_PALETTE, "&Palette", "")
        self.view_menu.AppendSeparator()
        self.view_menu.Append(ID_MORE, "&More", "")
        """

        self.menuBar().addMenu(self.view_menu)

        help_menu = QMenu("Help")
        """
        help_menu.Append(ID_ENEMY_COMPATIBILITY, "&Enemy Compatibility", "")
        help_menu.Append(ID_TROUBLESHOOTING, "&Troubleshooting", "")
        help_menu.AppendSeparator()
        help_menu.Append(ID_PROGRAM_WEBSITE, "&Program Website", "")
        help_menu.Append(ID_MAKE_A_DONATION, "&Make a Donation", "")
        help_menu.AppendSeparator()
        """
        update_action = help_menu.addAction("Check for updates")
        update_action.triggered.connect(self.on_check_for_update)

        help_menu.addSeparator()

        video_action = help_menu.addAction("Feature Video on YouTube")
        video_action.triggered.connect(lambda: open_url(feature_video_link))

        github_action = help_menu.addAction("Github Repository")
        github_action.triggered.connect(lambda: open_url(github_link))

        discord_action = help_menu.addAction("SMB3 Rom Hacking Discord")
        discord_action.triggered.connect(lambda: open_url(discord_link))

        help_menu.addSeparator()

        enemy_compat_action = help_menu.addAction("Enemy Compatibility")
        enemy_compat_action.triggered.connect(lambda: open_url(enemy_compat_link))

        about_action = help_menu.addAction("&About")
        about_action.triggered.connect(self.on_about)

        self.menuBar().addMenu(help_menu)

        self.block_viewer = None
        self.object_viewer = None

        self.level_ref = LevelRef()
        self.level_ref.data_changed.connect(self._on_level_data_changed)

        self.context_menu = ContextMenu(self.level_ref)
        self.context_menu.triggered.connect(self.on_menu)

        self.level_view = LevelView(self, self.level_ref, self.context_menu)

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

        self.menu_toolbar.addAction(icon("settings.svg"), "Editor Settings").triggered.connect(self._on_show_settings)
        self.menu_toolbar.addSeparator()
        self.menu_toolbar.addAction(icon("folder.svg"), "Open ROM").triggered.connect(self.on_open_rom)
        self.menu_toolbar_save_action = self.menu_toolbar.addAction(icon("save.svg"), "Save Level")
        self.menu_toolbar_save_action.triggered.connect(self.on_save_rom)
        self.menu_toolbar.addSeparator()

        self.undo_action = self.menu_toolbar.addAction(icon("rotate-ccw.svg"), "Undo Action")
        self.undo_action.triggered.connect(self.level_ref.undo)
        self.undo_action.setEnabled(False)
        self.redo_action = self.menu_toolbar.addAction(icon("rotate-cw.svg"), "Redo Action")
        self.redo_action.triggered.connect(self.level_ref.redo)
        self.redo_action.setEnabled(False)

        self.menu_toolbar.addSeparator()
        play_action = self.menu_toolbar.addAction(icon("play-circle.svg"), "Play Level")
        play_action.triggered.connect(self.on_play)
        play_action.setWhatsThis("Opens an emulator with the current Level set to 1-1.\nSee Settings.")
        self.menu_toolbar.addSeparator()
        self.menu_toolbar.addAction(icon("zoom-out.svg"), "Zoom Out").triggered.connect(self.level_view.zoom_out)
        self.menu_toolbar.addAction(icon("zoom-in.svg"), "Zoom In").triggered.connect(self.level_view.zoom_in)
        self.menu_toolbar.addSeparator()
        header_action = self.menu_toolbar.addAction(icon("tool.svg"), "Edit Level Header")
        header_action.triggered.connect(self.on_header_editor)
        header_action.setWhatsThis(
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

        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_Z), self, self.level_ref.undo)
        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_Y), self, self.level_ref.redo)
        QShortcut(QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_Z), self, self.level_ref.redo)

        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_Plus), self, self.level_view.zoom_in)
        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_Minus), self, self.level_view.zoom_out)

        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_A), self, self.level_view.select_all)
        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_L), self, self.object_dropdown.setFocus)

        self.on_open_rom(path_to_rom)

        self.showMaximized()

    def _on_new_level(self):
        if not self.safe_to_change():
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
        self.undo_action.setEnabled(self.level_ref.undo_stack.undo_available)
        self.redo_action.setEnabled(self.level_ref.undo_stack.redo_available)

        self.jump_destination_action.setEnabled(self.level_ref.level.has_next_area)

        level_has_changed = self.level_ref.level.changed and not self.level_ref.level.undo_stack.is_empty
        level_is_m3l = not self.level_ref.level.attached_to_rom

        self.menu_toolbar_save_action.setEnabled(level_has_changed or level_is_m3l or PaletteGroup.changed)

        self._save_auto_data()

    def _on_show_settings(self):
        SettingsDialog(self).exec_()

    @staticmethod
    def _save_auto_rom():
        ROM().save_to_file(auto_save_rom_path, set_new_path=False)

    def _save_auto_data(self):
        undo_index, data = self.level_ref.level.undo_stack.export_data()

        (level_offset, _), (enemy_offset, _) = self.level_ref.level.to_bytes()

        object_set_number = self.level_ref.level.object_set_number

        base64_data = []

        for (object_offset, object_data), (enemy_offset_, enemy_data) in data:
            base64_data.append(
                (
                    object_offset,
                    base64.b64encode(object_data).decode("ascii"),
                    enemy_offset_,
                    base64.b64encode(enemy_data).decode("ascii"),
                )
            )

        with open(auto_save_level_data_path, "w") as level_data_file:
            level_data_file.write(
                json.dumps([object_set_number, level_offset, enemy_offset, (undo_index, base64_data)])
            )

    def _load_auto_save(self):
        # rom already loaded
        with open(auto_save_level_data_path, "r") as level_data_file:
            json_data = level_data_file.read()

            object_set_number, level_offset, enemy_offset, (undo_index, base64_data) = json.loads(json_data)

        # load level from ROM, or from m3l file
        if level_offset == enemy_offset == 0:
            if not auto_save_m3l_path.exists():
                QMessageBox.critical(
                    self,
                    "Failed loading auto save",
                    "Could not recover m3l file, that was edited, when the editor crashed.",
                )

            with open(auto_save_m3l_path, "rb") as m3l_file:
                self.load_m3l(bytearray(m3l_file.read()), auto_save_m3l_path)
        else:
            self.update_level("recovered level", level_offset, enemy_offset, object_set_number)

        # restore undo/redo stack
        byte_data = []
        for undo_data in base64_data:
            level_offset, object_data, enemy_offset, enemy_data = undo_data

            object_data = bytearray(base64.b64decode(object_data))
            enemy_data = bytearray(base64.b64decode(enemy_data))

            byte_data.append(((level_offset, object_data), (enemy_offset, enemy_data)))

        self.level_ref.level.changed = bool(base64_data)
        self.level_ref.import_undo_stack_data(undo_index, byte_data)

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

        arguments = SETTINGS["instaplay_arguments"].replace("%f", str(path_to_temp_rom))
        arguments = shlex.split(arguments, posix=False)

        emu_path = pathlib.Path(SETTINGS["instaplay_emulator"])

        if emu_path.is_absolute():
            if emu_path.exists():
                emulator = str(emu_path)
            else:
                QMessageBox.critical(
                    self, "Emulator not found", f"Check it under File > Settings.\nFile {emu_path} not found."
                )
                return
        else:
            emulator = SETTINGS["instaplay_emulator"]

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

        header_editor.exec_()

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
        *_, powerup, hasPWing = POWERUPS[SETTINGS["default_powerup"]]

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

    def on_screenshot(self, _) -> bool:
        if self.level_view is None:
            return False

        recommended_file = f"{os.path.expanduser('~')}/{ROM.name} - {self.level_view.level_ref.name}.png"

        pathname, _ = QFileDialog.getSaveFileName(
            self, caption="Save Screenshot", dir=recommended_file, filter=IMG_FILE_FILTER
        )

        if not pathname:
            return False

        # Proceed loading the file chosen by the user
        self.level_view.make_screenshot().save(pathname)

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
                return False

        # Proceed loading the file chosen by the user
        try:
            ROM.load_from_file(path_to_rom)

            if path_to_rom == auto_save_rom_path:
                self._load_auto_save()
            else:
                self._save_auto_rom()
                return self.open_level_selector(None)

        except IOError as exp:
            QMessageBox.warning(self, type(exp).__name__, f"Cannot open file '{path_to_rom}'.")
            return False
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

        self.level_ref.level.from_m3l(m3l_data)

        self.level_view.level_ref.name = os.path.basename(pathname)

        self.update_gui_for_level()

    def safe_to_change(self) -> bool:
        if not self.level_ref:
            return True

        if self.level_ref.level.changed:
            answer = QMessageBox.question(
                self,
                "Please confirm",
                "Current content has not been saved! Proceed?",
                QMessageBox.No | QMessageBox.Yes,
                QMessageBox.No,
            )

            if answer == QMessageBox.No:
                return False

        return self._ask_for_palette_save()

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

            answer = level_selector.exec_()

            if answer == QMessageBox.Accepted:
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

                self.level_view.level_ref.attach_to_rom(
                    level_selector.object_data_offset, level_selector.enemy_data_offset
                )

                if is_save_as:
                    # if we save to another rom, don't consider the level
                    # attached (to the current rom)
                    self.level_view.level_ref.attached_to_rom = False
                else:
                    # the m3l is saved to the current ROM, we can get rid of the auto save
                    auto_save_m3l_path.unlink(missing_ok=True)
            else:
                return

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
            self.level_ref.level.changed = False
            self.level_ref.data_changed.emit()

    def _save_current_changes_to_file(self, pathname: str, set_new_path):
        for offset, data in self.level_ref.to_bytes():
            ROM().bulk_write(data, offset)

        try:
            ROM().save_to_file(pathname, set_new_path)

            self._save_auto_rom()
        except IOError as exp:
            QMessageBox.warning(self, f"{type(exp).__name__}", f"Cannot save ROM data to file '{pathname}'.")

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

    def save_m3l(self, pathname: str, m3l_bytes: bytearray):
        try:
            with open(pathname, "wb") as m3l_file:
                m3l_file.write(m3l_bytes)
        except IOError as exp:
            QMessageBox.warning(self, type(exp).__name__, f"Couldn't save level to '{pathname}'.")

    def on_check_for_update(self):
        self.setCursor(Qt.WaitCursor)

        current_version = get_current_version_name()

        try:
            latest_version = get_latest_version_name()
        except ValueError as ve:
            QMessageBox.critical(self, "Error while checking for updates", f"Error: {ve}")
            self.setCursor(Qt.ArrowCursor)
            return

        if current_version != latest_version:
            latest_release_url = f"{releases_link}/tag/{latest_version}"

            go_to_github_button = QPushButton(icon("external-link.svg"), "Go to latest release")
            go_to_github_button.clicked.connect(lambda: open_url(latest_release_url))

            info_box = QMessageBox(
                QMessageBox.Information, "New release available", f"New Version {latest_version} is available."
            )

            info_box.addButton(QMessageBox.Cancel)
            info_box.addButton(go_to_github_button, QMessageBox.AcceptRole)

            info_box.exec_()
        else:
            QMessageBox.information(self, "No newer release", f"Version {current_version} is up to date.")

        self.setCursor(Qt.ArrowCursor)

    def on_menu(self, action: QAction):
        item_id = action.property(ID_PROP)

        if item_id in CHECKABLE_MENU_ITEMS:
            self.on_menu_item_checked(action)
            self.level_view.update()

            # if setting a checkbox, keep the menu open
            menu_of_action: QMenu = self.sender()
            menu_of_action.exec_()

        elif item_id in self.context_menu.get_all_menu_item_ids():
            x, y = self.context_menu.get_position()

            if item_id == CMAction.REMOVE:
                self.remove_selected_objects()
            elif item_id == CMAction.ADD_OBJECT:
                selected_object = self.object_dropdown.currentIndex()

                if selected_object != -1:
                    self.place_object_from_dropdown((x, y))
                else:
                    self.create_object_at(x, y)

            elif item_id == CMAction.CUT:
                self._cut_objects()
            elif item_id == CMAction.COPY:
                self._copy_objects()
            elif item_id == CMAction.PASTE:
                self._paste_objects(x, y)
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

    def _on_placeable_object_selected(self, level_object: Union[LevelObject, EnemyObject]):
        if self.sender() is self.object_toolbar:
            self.object_dropdown.select_object(level_object)
        else:
            self.object_toolbar.select_object(level_object)

    @undoable
    def bring_objects_to_foreground(self):
        self.level_ref.level.bring_to_foreground(self.level_ref.selected_objects)

    @undoable
    def bring_objects_to_background(self):
        self.level_ref.level.bring_to_background(self.level_ref.selected_objects)

    @undoable
    def create_object_at(self, x, y):
        self.level_view.create_object_at(x, y)

    @undoable
    def create_enemy_at(self, x, y):
        self.level_view.create_enemy_at(x, y)

    def _cut_objects(self):
        self._copy_objects()
        self.remove_selected_objects()

    def _copy_objects(self):
        selected_objects = self.level_view.get_selected_objects().copy()

        if selected_objects:
            self.context_menu.set_copied_objects(selected_objects)

    @undoable
    def _paste_objects(self, x=None, y=None):
        self.level_view.paste_objects_at(self.context_menu.get_copied_objects(), x, y)

    @undoable
    def remove_selected_objects(self):
        self.level_view.remove_selected_objects()
        self.level_view.update()
        self.spinner_panel.disable_all()

    def on_menu_item_checked(self, action: QAction):
        item_id = action.property(ID_PROP)

        checked = action.isChecked()

        if item_id == ID_GRID_LINES:
            self.level_view.draw_grid = checked
        elif item_id == ID_TRANSPARENCY:
            self.level_view.transparency = checked
        elif item_id == ID_JUMPS:
            self.level_view.draw_jumps = checked
        elif item_id == ID_MARIO:
            self.level_view.draw_mario = checked
        elif item_id == ID_RESIZE_TYPE:
            self.level_view.draw_expansions = checked
        elif item_id == ID_JUMP_OBJECTS:
            self.level_view.draw_jumps_on_objects = checked
        elif item_id == ID_ITEM_BLOCKS:
            self.level_view.draw_items_in_blocks = checked
        elif item_id == ID_INVISIBLE_ITEMS:
            self.level_view.draw_invisible_items = checked
        elif item_id == ID_AUTOSCROLL:
            self.level_view.draw_autoscroll = checked

        SETTINGS["draw_mario"] = self.level_view.draw_mario
        SETTINGS["draw_jumps"] = self.level_view.draw_jumps
        SETTINGS["draw_grid"] = self.level_view.draw_grid
        SETTINGS["draw_expansion"] = self.level_view.draw_expansions
        SETTINGS["draw_jump_on_objects"] = self.level_view.draw_jumps_on_objects
        SETTINGS["draw_items_in_blocks"] = self.level_view.draw_items_in_blocks
        SETTINGS["draw_invisible_items"] = self.level_view.draw_invisible_items
        SETTINGS["draw_autoscroll"] = self.level_view.draw_autoscroll
        SETTINGS["block_transparency"] = self.level_view.transparency

        save_settings()

    @undoable
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

            self.level_view.replace_object(selected_object, domain, obj_type, length)
        else:
            self.level_view.replace_enemy(selected_object, obj_type)

        self.level_ref.data_changed.emit()

    def fill_object_list(self):
        self.object_list.Clear()

        self.object_list.SetItems(self.level_view.get_object_names())

    def open_level_selector(self, _):
        if not self.safe_to_change():
            return

        level_selector = LevelSelector(self)

        level_was_selected = level_selector.exec_() == QDialog.Accepted

        if level_was_selected:
            self.update_level(
                level_selector.level_name,
                level_selector.object_data_offset,
                level_selector.enemy_data_offset,
                level_selector.object_set,
            )

        return level_was_selected

    def on_block_viewer(self, _):
        if self.block_viewer is None:
            self.block_viewer = BlockViewer(parent=self)

        if self.level_ref.level is not None:
            self.block_viewer.object_set = self.level_ref.object_set.number
            self.block_viewer.palette_group = self.level_ref.object_palette_index

        self.block_viewer.show()

    def on_object_viewer(self, _):
        if self.object_viewer is None:
            self.object_viewer = ObjectViewer(parent=self)

        if self.level_ref.level is not None:
            object_set = self.level_ref.object_set.number
            graphics_set = self.level_ref.graphic_set

            self.object_viewer.set_object_and_graphic_set(object_set, graphics_set)

            if len(self.level_view.get_selected_objects()) == 1:
                selected_object = self.level_view.get_selected_objects()[0]

                if isinstance(selected_object, LevelObject):
                    self.object_viewer.set_object(
                        selected_object.domain, selected_object.obj_index, selected_object.length
                    )

        self.object_viewer.show()

    def on_palette_viewer(self, _):
        PaletteViewer(self, self.level_ref).exec_()

    def on_edit_autoscroll(self, _):
        AutoScrollEditor(self, self.level_ref).exec_()

    def on_header_editor(self, _):
        HeaderEditor(self, self.level_ref).exec_()

    def update_level(self, level_name: str, object_data_offset: int, enemy_data_offset: int, object_set: int):
        try:
            self.level_ref.load_level(level_name, object_data_offset, enemy_data_offset, object_set)
        except IndexError:
            QMessageBox.critical(self, "Please confirm", "Failed loading level. The level offsets don't match.")

            return

        self.update_gui_for_level()

    def update_gui_for_level(self):
        self._enable_disable_gui_elements()

        self.update_title()
        self.jump_list.update()

        is_a_world_map = isinstance(self.level_ref.level, WorldMap)

        self.save_m3l_action.setEnabled(not is_a_world_map)
        self.edit_header_action.setEnabled(not is_a_world_map)

        if is_a_world_map:
            self.object_dropdown.Clear()
            self.object_dropdown.setEnabled(False)

            self.jump_list.setEnabled(False)
            self.jump_list.Clear()
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
        level_elements.remove(self.select_level_action)
        level_elements.remove(self.new_level_action)

        level_elements.extend(self.object_menu.actions())
        level_elements.extend(self.view_menu.actions())

        for gui_element in rom_elements:
            gui_element.setEnabled(ROM.is_loaded())

        for gui_element in level_elements:
            gui_element.setEnabled(ROM.is_loaded() and self.level_ref.fully_loaded)

    def on_jump_edit(self):
        index = self.jump_list.currentIndex().row()

        updated_jump = JumpEditor.edit_jump(self, self.level_view.level_ref.jumps[index])

        self.on_jump_edited(updated_jump)

    @undoable
    def on_jump_added(self):
        self.level_view.add_jump()

    @undoable
    def on_jump_removed(self):
        self.level_view.remove_jump(self.jump_list.currentIndex().row())

    @undoable
    def on_jump_edited(self, jump):
        index = self.jump_list.currentIndex().row()

        assert index >= 0

        if isinstance(self.level_ref.level, Level):
            self.level_view.level_ref.jumps[index] = jump
            self.jump_list.item(index).setText(str(jump))

    def on_jump_list_change(self, event):
        self.jump_list.set_jumps(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MiddleButton:
            pos = self.level_view.mapFromGlobal(self.mapToGlobal(event.pos())).toTuple()

            self.place_object_from_dropdown(pos)

    @undoable
    def place_object_from_dropdown(self, pos: Tuple[int, int]) -> None:
        # the dropdown is synchronized with the toolbar, so it doesn't matter where to take it from
        level_object = self.object_dropdown.currentData(Qt.UserRole)

        self.object_toolbar.add_recent_object(level_object)

        if isinstance(level_object, LevelObject):
            self.level_view.create_object_at(*pos, level_object.domain, level_object.obj_index)
        elif isinstance(level_object, EnemyObject):
            self.level_view.add_enemy(level_object.obj_index, *pos, -1)

    def on_about(self, _):
        about = AboutDialog(self)

        about.show()

    def closeEvent(self, event: QCloseEvent):
        if not self.safe_to_change():
            event.ignore()

            return

        auto_save_rom_path.unlink(missing_ok=True)
        auto_save_m3l_path.unlink(missing_ok=True)
        auto_save_level_data_path.unlink(missing_ok=True)

        super(MainWindow, self).closeEvent(event)
