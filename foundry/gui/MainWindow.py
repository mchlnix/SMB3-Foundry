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
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QShortcut,
    QSizePolicy,
    QSplitter,
    QToolBar,
)

from foundry import (
    discord_link,
    feature_video_link,
    get_current_version_name,
    get_latest_version_name,
    icon,
    open_url,
    releases_link,
)
from foundry.game.File import ROM
from foundry.game.gfx.objects.EnemyItem import EnemyObject
from foundry.game.gfx.objects.LevelObject import LevelObject
from foundry.game.level.Level import Level
from foundry.game.level.LevelRef import LevelRef
from foundry.game.level.WorldMap import WorldMap
from foundry.gui.AboutWindow import AboutDialog
from foundry.gui.BlockViewer import BlockViewer
from foundry.gui.ContextMenu import CMAction, ContextMenu
from foundry.gui.HeaderEditor import HeaderEditor
from foundry.gui.JumpEditor import JumpEditor
from foundry.gui.JumpList import JumpList
from foundry.gui.LevelSelector import LevelSelector
from foundry.gui.LevelSizeBar import LevelSizeBar
from foundry.gui.LevelView import LevelView, undoable
from foundry.gui.ObjectDropdown import ObjectDropdown
from foundry.gui.ObjectList import ObjectList
from foundry.gui.ObjectStatusBar import ObjectStatusBar
from foundry.gui.ObjectToolBar import ObjectToolBar
from foundry.gui.ObjectViewer import ObjectViewer
from foundry.gui.SettingsDialog import show_settings
from foundry.gui.SpinnerPanel import SpinnerPanel
from foundry.gui.settings import SETTINGS, save_settings
from smb3parse.constants import TILE_LEVEL_1
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

CHECKABLE_MENU_ITEMS = [
    ID_TRANSPARENCY,
    ID_GRID_LINES,
    ID_JUMPS,
    ID_MARIO,
    ID_RESIZE_TYPE,
    ID_JUMP_OBJECTS,
    ID_ITEM_BLOCKS,
    ID_INVISIBLE_ITEMS,
]

ID_PROP: bytes = "ID"  # the stubs for setProperty are wrong so keep the warning to this line

# mouse modes

MODE_FREE = 0
MODE_DRAG = 1
MODE_RESIZE = 2


class MainWindow(QMainWindow):
    def __init__(self, path_to_rom=""):
        super(MainWindow, self).__init__()

        self.setWindowIcon(icon("foundry.ico"))

        file_menu = QMenu("File")

        open_rom_action = file_menu.addAction("&Open ROM")
        open_rom_action.triggered.connect(self.on_open_rom)
        self.open_m3l_action = file_menu.addAction("&Open M3L")
        self.open_m3l_action.triggered.connect(self.on_open_m3l)

        file_menu.addSeparator()

        save_rom_action = file_menu.addAction("&Save ROM")
        save_rom_action.triggered.connect(self.on_save_rom)
        save_rom_as_action = file_menu.addAction("&Save ROM as ...")
        save_rom_as_action.triggered.connect(self.on_save_rom_as)
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
        settings_action.triggered.connect(show_settings)
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

        level_menu = QMenu("Level")

        select_level_action = level_menu.addAction("&Select Level")
        select_level_action.triggered.connect(self.open_level_selector)

        """
        level_menu.Append(ID_GOTO_NEXT_AREA, "&Go to next Area", "")
        level_menu.AppendSeparator()
        """
        self.reload_action = level_menu.addAction("&Reload Level")
        self.reload_action.triggered.connect(self.reload_level)
        level_menu.addSeparator()
        self.edit_header_action = level_menu.addAction("&Edit Header")
        self.edit_header_action.triggered.connect(self.on_header_editor)
        """
        level_menu.Append(ID_EDIT_POINTERS, "&Edit Pointers", "")
        """

        self.menuBar().addMenu(level_menu)

        object_menu = QMenu("Objects")

        view_blocks_action = object_menu.addAction("&View Blocks")
        view_blocks_action.triggered.connect(self.on_block_viewer)
        view_objects_action = object_menu.addAction("&View Objects")
        view_objects_action.triggered.connect(self.on_object_viewer)
        """
        object_menu.AppendSeparator()
        object_menu.Append(ID_CLONE_OBJECT_ENEMY, "&Clone Object/Enemy", "")
        object_menu.AppendSeparator()
        object_menu.Append(ID_ADD_3_BYTE_OBJECT, "&Add 3 Byte Object", "")
        object_menu.Append(ID_ADD_4_BYTE_OBJECT, "&Add 4 Byte Object", "")
        object_menu.Append(ID_ADD_ENEMY, "&Add Enemy", "")
        object_menu.AppendSeparator()
        object_menu.Append(ID_DELETE_OBJECT_ENEMY, "&Delete Object/Enemy", "")
        object_menu.Append(ID_DELETE_ALL, "&Delete All", "")
        """

        self.menuBar().addMenu(object_menu)

        view_menu = QMenu("View")
        view_menu.triggered.connect(self.on_menu)

        action = view_menu.addAction("Mario")
        action.setProperty(ID_PROP, ID_MARIO)
        action.setCheckable(True)
        action.setChecked(SETTINGS["draw_mario"])

        action = view_menu.addAction("&Jumps on objects")
        action.setProperty(ID_PROP, ID_JUMP_OBJECTS)
        action.setCheckable(True)
        action.setChecked(SETTINGS["draw_jump_on_objects"])

        action = view_menu.addAction("Items in blocks")
        action.setProperty(ID_PROP, ID_ITEM_BLOCKS)
        action.setCheckable(True)
        action.setChecked(SETTINGS["draw_items_in_blocks"])

        action = view_menu.addAction("Invisible items")
        action.setProperty(ID_PROP, ID_INVISIBLE_ITEMS)
        action.setCheckable(True)
        action.setChecked(SETTINGS["draw_invisible_items"])

        view_menu.addSeparator()

        action = view_menu.addAction("Jump Zones")
        action.setProperty(ID_PROP, ID_JUMPS)
        action.setCheckable(True)
        action.setChecked(SETTINGS["draw_jumps"])

        action = view_menu.addAction("&Grid lines")
        action.setProperty(ID_PROP, ID_GRID_LINES)
        action.setCheckable(True)
        action.setChecked(SETTINGS["draw_grid"])

        action = view_menu.addAction("Resize Type")
        action.setProperty(ID_PROP, ID_RESIZE_TYPE)
        action.setCheckable(True)
        action.setChecked(SETTINGS["draw_expansion"])

        view_menu.addSeparator()

        action = view_menu.addAction("&Block Transparency")
        action.setProperty(ID_PROP, ID_TRANSPARENCY)
        action.setCheckable(True)
        action.setChecked(SETTINGS["block_transparency"])

        view_menu.addSeparator()
        view_menu.addAction("&Save Screenshot of Level").triggered.connect(self.on_screenshot)
        """
        view_menu.Append(ID_BACKGROUND_FLOOR, "&Background & Floor", "")
        view_menu.Append(ID_TOOLBAR, "&Toolbar", "")
        view_menu.AppendSeparator()
        view_menu.Append(ID_ZOOM, "&Zoom", "")
        view_menu.AppendSeparator()
        view_menu.Append(ID_USE_ROM_GRAPHICS, "&Use ROM Graphics", "")
        view_menu.Append(ID_PALETTE, "&Palette", "")
        view_menu.AppendSeparator()
        view_menu.Append(ID_MORE, "&More", "")
        """

        self.menuBar().addMenu(view_menu)

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

        discord_action = help_menu.addAction("SMB3 Rom Hacking Discord")
        discord_action.triggered.connect(lambda: open_url(discord_link))

        help_menu.addSeparator()

        about_action = help_menu.addAction("&About")
        about_action.triggered.connect(self.on_about)

        self.menuBar().addMenu(help_menu)

        self.level_selector = LevelSelector(parent=self)

        self.block_viewer = None
        self.object_viewer = None

        self.level_ref = LevelRef()

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

        self.jump_list = JumpList(self, self.level_ref)
        self.jump_list.add_jump.connect(self.on_jump_added)
        self.jump_list.edit_jump.connect(self.on_jump_edit)
        self.jump_list.remove_jump.connect(self.on_jump_removed)

        splitter = QSplitter(self)
        splitter.setOrientation(Qt.Vertical)

        splitter.addWidget(self.object_list)
        splitter.setStretchFactor(0, 1)
        splitter.addWidget(self.jump_list)

        splitter.setChildrenCollapsible(False)

        level_toolbar = QToolBar("Level Info Toolbar", self)
        level_toolbar.setContextMenuPolicy(Qt.PreventContextMenu)
        level_toolbar.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        level_toolbar.setOrientation(Qt.Horizontal)
        level_toolbar.setFloatable(False)

        level_toolbar.addWidget(self.spinner_panel)
        level_toolbar.addWidget(self.object_dropdown)
        level_toolbar.addWidget(self.level_size_bar)
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

        menu_toolbar = QToolBar("Menu Toolbar", self)
        menu_toolbar.setOrientation(Qt.Horizontal)
        menu_toolbar.setIconSize(QSize(20, 20))

        menu_toolbar.addAction(icon("settings.svg"), "Editor Settings").triggered.connect(show_settings)
        menu_toolbar.addSeparator()
        menu_toolbar.addAction(icon("folder.svg"), "Open ROM").triggered.connect(self.on_open_rom)
        menu_toolbar.addAction(icon("save.svg"), "Save Level").triggered.connect(self.on_save_rom)
        menu_toolbar.addSeparator()
        menu_toolbar.addAction(icon("rotate-ccw.svg"), "Undo Action")
        menu_toolbar.addAction(icon("rotate-cw.svg"), "Redo Action")
        menu_toolbar.addSeparator()
        menu_toolbar.addAction(icon("play-circle.svg"), "Play Level").triggered.connect(self.on_play)
        menu_toolbar.addSeparator()
        menu_toolbar.addAction(icon("zoom-out.svg"), "Zoom Out").triggered.connect(self.level_view.zoom_out)
        menu_toolbar.addAction(icon("zoom-in.svg"), "Zoom In").triggered.connect(self.level_view.zoom_in)
        menu_toolbar.addSeparator()
        menu_toolbar.addAction(icon("tool.svg"), "Edit Level Header").triggered.connect(self.on_header_editor)
        menu_toolbar.addAction(icon("arrow-right-circle.svg"), "Go to Jump Destination")
        menu_toolbar.addSeparator()
        menu_toolbar.addAction(icon("help-circle.svg"), "What's this?")

        self.addToolBar(Qt.TopToolBarArea, menu_toolbar)

        self.status_bar = ObjectStatusBar(self, self.level_ref)
        self.setStatusBar(self.status_bar)

        self.delete_shortcut = QShortcut(QKeySequence(Qt.Key_Delete), self, self.remove_selected_objects)

        self.cut_shortcut = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_X), self, self._cut_objects)
        self.copy_shortcut = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_C), self, self._copy_objects)
        self.paste_shortcut = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_V), self, self._paste_objects)

        self.undo_shortcut = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_Z), self, self.spinner_panel.on_undo)
        self.redo_shortcut = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_Y), self, self.spinner_panel.on_redo)
        self.redo_shortcut_alt = QShortcut(
            QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_Z), self, self.spinner_panel.on_redo
        )

        self.zoom_in_shortcut = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_Plus), self, self.level_view.zoom_in)
        self.zoom_out_shortcut = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_Minus), self, self.level_view.zoom_out)

        self.select_all_shortcut = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_A), self, self.level_view.select_all)

        if not self.on_open_rom(path_to_rom):
            self.deleteLater()

        self.showMaximized()

    def on_play(self):
        """
        Copies the ROM, including the current level, to a temporary directory, saves the current level as level 1-1 and
        opens the rom in an emulator.
        """
        temp_dir = pathlib.Path(tempfile.gettempdir()) / "smb3foundry"
        temp_dir.mkdir(parents=True, exist_ok=True)

        path_to_temp_rom = temp_dir / "instaplay.rom"

        ROM().save_to(path_to_temp_rom)

        if not self._put_current_level_to_level_1_1(path_to_temp_rom):
            return

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

    def _put_current_level_to_level_1_1(self, path_to_rom) -> bool:
        with open(path_to_rom, "rb") as smb3_rom:
            data = smb3_rom.read()

        rom = SMB3Rom(bytearray(data))

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

        # save rom
        rom.save_to(path_to_rom)

        return True

    def on_screenshot(self, _) -> bool:
        if self.level_view is None:
            return False

        recommended_file = f"{os.path.expanduser('~')}/{ROM.name} - {self.level_view.level_ref.name}.png"

        pathname, _ = QFileDialog.getSaveFileName(
            self, caption="Save Screenshot", dir=recommended_file, filter=IMG_FILE_FILTER
        )

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
                return False

        # Proceed loading the file chosen by the user
        try:
            ROM.load_from_file(path_to_rom)

            return self.open_level_selector(None)

        except IOError as exp:
            QMessageBox.warning(self, type(exp).__name__, f"Cannot open file '{path_to_rom}'.")
            return False

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

                self.level_view.from_m3l(bytearray(m3l_file.read()))
        except IOError as exp:
            QMessageBox.warning(self, type(exp).__name__, f"Cannot open file '{pathname}'.")

            return False

        self.level_view.level_ref.name = os.path.basename(pathname)

        self.set_up_gui_for_level()

        return True

    def safe_to_change(self) -> bool:
        if not self.level_ref:
            return True

        if self.level_ref.changed:
            answer = QMessageBox.question(
                self,
                "Please confirm",
                "Current content has not been saved! Proceed?",
                QMessageBox.No | QMessageBox.Yes,
                QMessageBox.No,
            )

            return answer == QMessageBox.Yes
        else:
            return True

    def on_save_rom(self, _):
        self.save_rom(False)

    def on_save_rom_as(self, _):
        self.save_rom(True)

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

        if not self.level_view.level_ref.attached_to_rom:
            QMessageBox.information(
                self,
                "Importing M3L into ROM",
                "Please select the positions in the ROM you want the level objects and enemies/items to be stored.",
                QMessageBox.Ok,
            )

            answer = self.level_selector.exec_()

            if answer == QMessageBox.Accepted:
                self.level_view.level_ref.attach_to_rom(
                    self.level_selector.object_data_offset, self.level_selector.enemy_data_offset
                )

                if is_save_as:
                    # if we save to another rom, don't consider the level
                    # attached (to the current rom)
                    self.level_view.level_ref.attached_to_rom = False
            else:
                return

        if is_save_as:
            pathname, _ = QFileDialog.getSaveFileName(self, caption="Save ROM as", filter=ROM_FILE_FILTER)
            if pathname is None:
                return  # the user changed their mind
        else:
            pathname = ROM.path

        level = self.level_view.level_ref

        for offset, data in level.to_bytes():
            ROM().bulk_write(data, offset)

        try:
            ROM().save_to_file(pathname)
        except IOError as exp:
            QMessageBox.warning(self, f"{type(exp).__name__}", f"Cannot save ROM data to file '{pathname}'.")

        self.update_title()

        self.level_view.level_ref.changed = False

    def on_save_m3l(self, _):
        suggested_file = self.level_view.level_ref.name

        if not suggested_file.endswith(".m3l"):
            suggested_file += ".m3l"

        pathname, _ = QFileDialog.getSaveFileName(self, caption="Save M3L as", filter=M3L_FILE_FILTER)

        if not pathname:
            return

        level = self.level_view.level_ref

        try:
            with open(pathname, "wb") as m3l_file:
                m3l_file.write(level.to_m3l())
        except IOError as exp:
            QMessageBox.warning(self, type(exp).__name__, f"Couldn't save level to '{pathname}'.")

    def on_check_for_update(self):
        self.setCursor(Qt.WaitCursor)

        current_version = get_current_version_name()

        try:
            latest_version = get_latest_version_name()
        except ValueError as ve:
            QMessageBox.critical(self, "Error while checking for updates", f"Error: {ve}")
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

        world = self.level_view.level_ref.world
        level = self.level_view.level_ref.level_number
        object_data = self.level_view.level_ref.header_offset
        enemy_data = self.level_view.level_ref.enemy_offset
        object_set = self.level_view.level_ref.object_set_number

        self.update_level(world, level, object_data, enemy_data, object_set)

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

        SETTINGS["draw_mario"] = self.level_view.draw_mario
        SETTINGS["draw_jumps"] = self.level_view.draw_jumps
        SETTINGS["draw_grid"] = self.level_view.draw_grid
        SETTINGS["draw_expansion"] = self.level_view.draw_expansions
        SETTINGS["draw_jump_on_objects"] = self.level_view.draw_jumps_on_objects
        SETTINGS["draw_items_in_blocks"] = self.level_view.draw_items_in_blocks
        SETTINGS["draw_invisible_items"] = self.level_view.draw_invisible_items
        SETTINGS["block_transparency"] = self.level_view.transparency

        save_settings()

    @undoable
    def on_spin(self, _):
        selected_objects = self.level_ref.selected_objects

        assert len(selected_objects) == 1, print(selected_objects)

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

        level_was_selected = self.level_selector.exec_() == QDialog.Accepted

        if level_was_selected:
            self.update_level(
                self.level_selector.selected_world,
                self.level_selector.selected_level,
                self.level_selector.object_data_offset,
                self.level_selector.enemy_data_offset,
                self.level_selector.object_set,
            )

        return level_was_selected

    def on_block_viewer(self, _):
        if self.block_viewer is None:
            self.block_viewer = BlockViewer(parent=self)

        self.block_viewer.show()

    def on_object_viewer(self, _):
        if self.object_viewer is None:
            self.object_viewer = ObjectViewer(parent=self)

        self.object_viewer.show()

    def on_header_editor(self, _):
        HeaderEditor(self, self.level_ref).exec_()

    def update_level(self, world: int, level: int, object_data_offset: int, enemy_data_offset: int, object_set: int):
        try:
            self.level_ref.load_level(world, level, object_data_offset, enemy_data_offset, object_set)
        except IndexError:
            QMessageBox.critical(self, "Please confirm", "Failed loading level. The level offsets don't match.")

            return

        self.set_up_gui_for_level()

    def set_up_gui_for_level(self):
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

        super(MainWindow, self).closeEvent(event)
