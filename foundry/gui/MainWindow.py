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
    QWhatsThis,
)

from foundry import (
    discord_link,
    feature_video_link,
    get_current_version_name,
    get_latest_version_name,
    github_link,
    icon,
    open_url,
    releases_link,
)
from foundry.game.File import ROM
from foundry.game.gfx.objects.EnemyItem import EnemyObject
from foundry.game.gfx.objects.LevelObjectController import LevelObjectController
from foundry.game.level.Level import Level, world_and_level_for_level_address
from foundry.game.level.LevelRef import LevelRef
from foundry.game.level.WorldMap import WorldMap
from foundry.gui.AboutWindow import AboutDialog
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
from foundry.gui.ObjectStatusBar import ObjectStatusBar
from foundry.gui.ObjectToolBar import ObjectToolBar
from foundry.gui.ObjectViewer import ObjectViewer
from foundry.gui.SettingsDialog import show_settings, get_gui_style
from foundry.gui.SpinnerPanel import SpinnerPanel
from foundry.gui.settings import save_settings, set_setting, get_setting
from smb3parse.constants import TILE_LEVEL_1
from smb3parse.levels.world_map import WorldMap as SMB3World
from smb3parse.util.rom import Rom as SMB3Rom
from foundry.gui.QMenus.Menu.Menu import Menu
from foundry.core.Action.ActionSelectFileToOpen import ActionSelectFileToOpen
from foundry.core.Action.ActionSafe import ActionSafe
from foundry.core.util import ROM_FILE_FILTER
from foundry.game.File import load_from_file
from foundry.gui.QMenus.Menu.MenuFile import FileMenu
from foundry.gui.QMenus.Menu.MenuHelp import HelpMenu
from foundry.gui.QMenus.MenuAction.MenuActionSettings import MenuActionSettings


ROM_FILE_FILTER = "ROM files (*.nes *.rom);;All files (*)"
M3L_FILE_FILTER = "M3L files (*.m3l);;All files (*)"
ASM6_FILE_FILER = "ASM files (*.asm);; All files (*)"
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
ID_BACKGROUND_ENABLED = 515

ID_VISUAL_OBJECT_TOOLBAR = 600
ID_OBJECT_ATTRIBUTE_TOOLBAR = 601
ID_COMPACT_TOOLBAR = 602
ID_BYTES_COUNTER_TOOLBAR = 603
ID_OBJECT_LIST_TOOLBAR = 604

CHECKABLE_MENU_ITEMS = [
    ID_TRANSPARENCY,
    ID_GRID_LINES,
    ID_JUMPS,
    ID_MARIO,
    ID_RESIZE_TYPE,
    ID_JUMP_OBJECTS,
    ID_ITEM_BLOCKS,
    ID_INVISIBLE_ITEMS,
    ID_BACKGROUND_ENABLED,
    ID_VISUAL_OBJECT_TOOLBAR,
    ID_OBJECT_ATTRIBUTE_TOOLBAR,
    ID_COMPACT_TOOLBAR,
    ID_BYTES_COUNTER_TOOLBAR,
    ID_OBJECT_LIST_TOOLBAR,
]

ID_PROP: bytes = "ID"  # the stubs for setProperty are wrong so keep the warning to this line

# mouse modes

MODE_FREE = 0
MODE_DRAG = 1
MODE_RESIZE = 2


class MainWindow(QMainWindow):
    def __init__(self, path_to_rom=""):
        super(MainWindow, self).__init__()

        self.setWindowIcon(icon("tanooki.ico"))
        self.setStyleSheet(get_gui_style())

        self.file_menu = FileMenu(self)
        self.file_menu.open_rom_action._action.attach_warning(self.safe_to_change)
        self.file_menu.open_rom_action._action.attach_observer(load_from_file)
        self.file_menu.open_rom_action._action.attach_observer(self.open_level_selector)
        self.file_menu.open_m3l_action._action.attach_warning(self.safe_to_change)
        self.file_menu.open_m3l_action._action.attach_observer(self.open_m3l)
        self.file_menu.save_rom_action._action.attach_warning(self.safe_to_change)
        self.file_menu.save_rom_action._action.attach_requirement(lambda: self.can_save_rom(False))
        self.file_menu.save_rom_action._action.attach_observer(self.save_rom)
        self.file_menu.save_rom_as_action._action.attach_warning(self.safe_to_change)
        self.file_menu.save_rom_as_action._action.attach_requirement(lambda: self.can_save_rom(True))
        self.file_menu.save_rom_as_action._action.attach_observer(self.save_rom)
        self.file_menu.save_m3l_action._action.attach_observer(self.save_m3l)
        self.file_menu.save_asm6_action._action.attach_observer(self.save_asm6)
        self.menuBar().addMenu(self.file_menu)

        level_menu = QMenu("Level")

        select_level_action = level_menu.addAction("&Select Level")
        select_level_action.triggered.connect(self.open_level_selector)

        self.reload_action = level_menu.addAction("&Reload Level")
        self.reload_action.triggered.connect(self.reload_level)
        level_menu.addSeparator()
        self.edit_header_action = level_menu.addAction("&Edit Header")
        self.edit_header_action.triggered.connect(self.on_header_editor)

        self.menuBar().addMenu(level_menu)

        object_menu = QMenu("Objects")

        view_blocks_action = object_menu.addAction("&View Blocks")
        view_blocks_action.triggered.connect(self.on_block_viewer)
        view_objects_action = object_menu.addAction("&View Objects")
        view_objects_action.triggered.connect(self.on_object_viewer)

        self.menuBar().addMenu(object_menu)

        view_menu = Menu(parent=self, title="View")
        view_menu.triggered.connect(self.on_menu)

        action = MenuActionSettings(view_menu, "draw_mario", "Mario")
        action.add_observer(lambda value: setattr(self.level_view, "draw_mario", value))

        action = MenuActionSettings(view_menu, "draw_jump_on_objects", "Warps")
        action.add_observer(lambda value: setattr(self.level_view, "draw_jumps_on_objects", value))

        action = MenuActionSettings(view_menu, "draw_items_in_blocks", "Items in Blocks")
        action.add_observer(lambda value: setattr(self.level_view, "draw_items_in_blocks", value))

        action = MenuActionSettings(view_menu, "draw_invisible_items", "Invisible items")
        action.add_observer(lambda value: setattr(self.level_view, "draw_invisible_items", value))

        view_menu.addSeparator()

        action = MenuActionSettings(view_menu, "draw_jumps", "Jump Zones")
        action.add_observer(lambda value: setattr(self.level_view, "draw_jumps", value))

        action = MenuActionSettings(view_menu, "draw_grid", "Grid Lines")
        action.add_observer(lambda value: setattr(self.level_view, "draw_grid", value))

        action = MenuActionSettings(view_menu, "draw_expansion", "Reisze Type")
        action.add_observer(lambda value: setattr(self.level_view, "draw_expansions", value))

        view_menu.addSeparator()

        action = MenuActionSettings(view_menu, "block_transparency", "Block Transparency")
        action.add_observer(lambda value: setattr(self.level_view, "transparency", value))

        action = MenuActionSettings(view_menu, "background_enabled", "Background")
        action.add_observer(lambda value: setattr(self.level_view, "background_enabled", value))

        view_menu.addSeparator()
        view_menu.addAction("&Save Screenshot of Level").triggered.connect(self.on_screenshot)

        self.menuBar().addMenu(view_menu)

        tool_menu = Menu(parent=self, title="Tools")
        tool_menu.triggered.connect(self.on_menu)

        tool_menu.addSection("Object Selectors")

        action = MenuActionSettings(tool_menu, "visual_object_toolbar", "Visual Object Selector")
        #action.add_observer(self.visual_object_toolbar.toggleViewAction().trigger)

        action = MenuActionSettings(tool_menu, "compact_object_toolbar", "Compact Object Selector")
        #action.add_observer(self.compact_object_toolbar.toggleViewAction().trigger)

        action = MenuActionSettings(tool_menu, "object_attribute_toolbar", "Object Attribute Toolbar")
        #action.add_observer(self.object_attribute_toolbar.toggleViewAction().trigger)

        tool_menu.addSeparator()

        action = MenuActionSettings(tool_menu, "bytes_counter_toolbar", "Byte Counter")
        #action.add_observer(self.bytes_counter_toolbar.toggleViewAction().trigger)

        action = MenuActionSettings(tool_menu, "object_list_toolbar", "Object List")
        #action.add_observer(self.object_list_toolbar.toggleViewAction().trigger)

        self.menuBar().addMenu(tool_menu)

        self.menuBar().addMenu(HelpMenu(self))

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

        self.object_toolbar = ObjectToolBar(self)
        self.object_toolbar.object_selected.connect(self._on_placeable_object_selected)

        self.visual_object_toolbar = self.add_toolbox("Object Toolbar", self.object_toolbar, 1)
        if get_setting("visual_object_toolbar", True) != 0:
            self.visual_object_toolbar.toggleViewAction().trigger()

        self.compact_object_toolbar = self.add_toolbox("Object Dropdown Toolbar", self.object_dropdown, 2)
        if get_setting("compact_object_toolbar", True) != 0:
            self.compact_object_toolbar.toggleViewAction().trigger()

        self.object_attribute_toolbar = self.add_toolbox("Level Spinner Toolbar", self.spinner_panel, 2)
        if get_setting("object_attribute_toolbar", True) != 0:
            self.object_attribute_toolbar.toggleViewAction().trigger()

        self.bytes_counter_toolbar = self.add_toolbox("Size Toolbar", [self.level_size_bar, self.enemy_size_bar], 2)
        if get_setting("bytes_counter_toolbar", True) != 0:
            self.bytes_counter_toolbar.toggleViewAction().trigger()

        self.object_list_toolbar = self.add_toolbox("Level Info", splitter, 2)
        if get_setting("object_list_toolbar", True) != 0:
            self.object_list_toolbar.toggleViewAction().trigger()

        menu_toolbar = QToolBar("Menu Toolbar", self)
        menu_toolbar.setOrientation(Qt.Horizontal)
        menu_toolbar.setIconSize(QSize(20, 20))

        menu_toolbar.addAction(icon("settings.svg"), "Editor Settings").triggered.connect(lambda: show_settings(self))
        menu_toolbar.addSeparator()
        menu_toolbar.addAction(icon("folder.svg"), "Open ROM").triggered.connect(self.file_menu.open_rom_action.action)
        menu_toolbar.addAction(icon("save.svg"), "Save Level").triggered.connect(self.file_menu.save_rom_action.action)
        menu_toolbar.addSeparator()

        self.undo_action = menu_toolbar.addAction(icon("rotate-ccw.svg"), "Undo Action")
        self.undo_action.triggered.connect(self.level_ref.undo)
        self.undo_action.setEnabled(False)
        self.redo_action = menu_toolbar.addAction(icon("rotate-cw.svg"), "Redo Action")
        self.redo_action.triggered.connect(self.level_ref.redo)
        self.redo_action.setEnabled(False)

        menu_toolbar.addSeparator()
        play_action = menu_toolbar.addAction(icon("play-circle.svg"), "Play Level")
        play_action.triggered.connect(self.on_play)
        play_action.setWhatsThis("Opens an emulator with the current Level set to 1-1.\nSee Settings.")
        menu_toolbar.addSeparator()
        menu_toolbar.addAction(icon("zoom-out.svg"), "Zoom Out").triggered.connect(self.level_view.zoom_out)
        menu_toolbar.addAction(icon("zoom-in.svg"), "Zoom In").triggered.connect(self.level_view.zoom_in)
        menu_toolbar.addSeparator()
        header_action = menu_toolbar.addAction(icon("tool.svg"), "Edit Level Header")
        header_action.triggered.connect(self.on_header_editor)
        header_action.setWhatsThis(
            "<b>Header Editor</b><br/>"
            "Many configurations regarding the level are done in its header, like the length of "
            "the timer, or where and how Mario enters the level.<br/>"
        )

        self.jump_destination_action = menu_toolbar.addAction(icon("arrow-right-circle.svg"), "Go to Jump Destination")
        self.jump_destination_action.triggered.connect(self._go_to_jump_destination)
        self.jump_destination_action.setWhatsThis(
            "Opens the level, that can be reached from this one, e.g. by entering a pipe."
        )

        menu_toolbar.addSeparator()

        whats_this_action = QWhatsThis.createAction()
        whats_this_action.setWhatsThis("Click on parts of the editor, to receive help information.")
        whats_this_action.setIcon(icon("help-circle.svg"))
        whats_this_action.setText("Starts 'What's this?' mode")
        menu_toolbar.addAction(whats_this_action)

        self.addToolBar(Qt.TopToolBarArea, menu_toolbar)

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

        self.select_rom_action = ActionSelectFileToOpen("open_rom", ActionSafe, "Select ROM", ROM_FILE_FILTER)
        self.select_rom_action.attach_observer(load_from_file)
        self.select_rom_action.attach_observer(self.open_level_selector)

        if not self.select_rom_action.observable.observable():
            self.deleteLater()

        self.showMaximized()

    def _on_level_data_changed(self):
        self.undo_action.setEnabled(self.level_ref.undo_stack.undo_available)
        self.redo_action.setEnabled(self.level_ref.undo_stack.redo_available)

        self.jump_destination_action.setEnabled(self.level_ref.level.has_next_area)

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

        if not self._put_current_level_to_level_1_1(path_to_temp_rom):
            return

        arguments = get_setting("instaplay_arguments", "").replace("%f", str(path_to_temp_rom))
        arguments = shlex.split(arguments, posix=False)

        emu_path = pathlib.Path(get_setting("instaplay_emulator", ""))

        if emu_path.is_absolute():
            if emu_path.exists():
                emulator = str(emu_path)
            else:
                QMessageBox.critical(
                    self, "Emulator not found", f"Check it under File > Settings.\nFile {emu_path} not found."
                )
                return
        else:
            emulator = get_setting("instaplay_emulator", "")

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

        if not pathname:
            return False

        # Proceed loading the file chosen by the user
        self.level_view.make_screenshot().save(pathname)

        return True

    def update_title(self):
        if self.level_view.level_ref is not None and ROM() is not None:
            title = f"{self.level_view.level_ref.name} - {ROM().name}"
        else:
            title = "SMB3Foundry"

        self.setWindowTitle(title)

    def safe_to_change(self, *_) -> Tuple[bool, str, str]:
        """Determines if a file is save to change"""
        if not self.level_ref or not self.level_ref.level.changed:
            return True, '', ''
        else:
            return False, "Please confirm", "Current content has not been saved! Proceed?"

    def can_save_rom(self, is_save_as):
        """Determines if we can save the rom"""
        if not self.level_view.level_ref.attached_to_rom:
            QMessageBox.information(
                self,
                "Importing M3L into ROM",
                "Please select the positions in the ROM you want the level objects and enemies/items to be stored.",
                QMessageBox.Ok,
            )

            level_selector = LevelSelector(self)

            answer = level_selector.exec_()

            if answer == QMessageBox.Accepted:
                self.level_view.level_ref.attach_to_rom(
                    level_selector.object_data_offset, level_selector.enemy_data_offset
                )

                if is_save_as:
                    # if we save to another rom, don't consider the level
                    # attached (to the current rom)
                    self.level_view.level_ref.attached_to_rom = False
                    return False
            else:
                return True
        return True

    def safe_to_save(self):
        """Determines if it is safe to save"""
        return self.level_view.level_safe_to_save()

    def save_rom(self, path_to_rom: str) -> None:
        """Saves the ROM"""
        level = self.level_view.level_ref

        for offset, data in level.to_bytes():
            ROM().bulk_write(data, offset)

        ROM().save_to_file(path_to_rom)

    def open_m3l(self, path: str) -> None:
        """Opens a M3L"""
        with open(path, "rb") as m3l_file:
            self.level_view.from_m3l(bytearray(m3l_file.read()))

    def save_m3l(self, path_to_rom: str) -> None:
        """Saves a M3L"""
        level = self.level_view.level_ref
        with open(path_to_rom, "wb") as m3l_file:
            m3l_file.write(level.to_m3l())

    def save_asm6(self, path_to_rom: str) -> None:
        """Saves a ASM6 file"""
        level = self.level_view.level_ref
        with open(path_to_rom, "w+") as asm6_file:
            asm6_file.write(level.to_asm6())

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

        level_name = self.level_view.level_ref.name
        object_data = self.level_view.level_ref.header_offset
        enemy_data = self.level_view.level_ref.enemy_offset
        object_set = self.level_view.level_ref.object_set_number

        self.update_level(level_name, object_data, enemy_data, object_set)

    def _on_placeable_object_selected(self, level_object: Union[LevelObjectController, EnemyObject]):
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
        elif item_id == ID_BACKGROUND_ENABLED:
            self.level_view.background_enabled = checked
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
        elif item_id == ID_VISUAL_OBJECT_TOOLBAR:
            self.visual_object_toolbar.toggleViewAction().trigger()
            set_setting("visual_object_toolbar", not get_setting("visual_object_toolbar", True))
        elif item_id == ID_OBJECT_ATTRIBUTE_TOOLBAR:
            self.object_attribute_toolbar.toggleViewAction().trigger()
            set_setting("object_attribute_toolbar", not get_setting("object_attribute_toolbar", True))
        elif item_id == ID_COMPACT_TOOLBAR:
            self.compact_object_toolbar.toggleViewAction().trigger()
            set_setting("compact_object_toolbar", not get_setting("compact_object_toolbar", True))
        elif item_id == ID_BYTES_COUNTER_TOOLBAR:
            self.bytes_counter_toolbar.toggleViewAction().trigger()
            set_setting("bytes_counter_toolbar", not get_setting("bytes_counter_toolbar", True))
        elif item_id == ID_OBJECT_LIST_TOOLBAR:
            self.object_list_toolbar.toggleViewAction().trigger()
            set_setting("object_list_toolbar", not get_setting("object_list_toolbar", True))

        save_settings()

    @undoable
    def on_spin(self, _):
        selected_objects = self.level_ref.selected_objects

        assert len(selected_objects) == 1, print(selected_objects)

        selected_object = selected_objects[0]

        obj_type = self.spinner_panel.get_type()

        if isinstance(selected_object, LevelObjectController):
            domain = self.spinner_panel.get_domain()

            if selected_object.bytes == 4:
                length = self.spinner_panel.get_length()
            else:
                length = None
            if selected_object.bytes >= 5:
                length = self.spinner_panel.get_length()
                overflow = [self.spinner_panel.get_index()]
            else:
                overflow = None

            self.level_view.replace_object(selected_object, domain, obj_type, length, overflow=overflow)
        else:
            self.level_view.replace_enemy(selected_object, obj_type)

        self.level_ref.data_changed.emit()

    def fill_object_list(self):
        self.object_list.Clear()

        self.object_list.SetItems(self.level_view.get_object_names())

    def open_level_selector(self, *_):
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

                if isinstance(selected_object, LevelObjectController):
                    self.object_viewer.set_object(
                        selected_object.domain, selected_object.obj_index, selected_object.length
                    )

        self.object_viewer.show()

    def on_header_editor(self, _):
        HeaderEditor(self, self.level_ref).exec_()

    def update_level(self, level_name: str, object_data_offset: int, enemy_data_offset: int, object_set: int):
        try:
            self.level_ref.load_level(level_name, object_data_offset, enemy_data_offset, object_set)
        except IndexError:
            QMessageBox.critical(self, "Please confirm", "Failed loading level. The level offsets don't match.")
        self.set_up_gui_for_level()

    def set_up_gui_for_level(self):
        self.update_title()
        self.jump_list.update()

        is_a_world_map = isinstance(self.level_ref.level, WorldMap)

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

        if isinstance(level_object, LevelObjectController):
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

    def force_update_level_view(self):
        self.level_view.paintEvent(0, True)

    def add_toolbox(self, name, widget, side):
        toolbar = QToolBar(name, self)
        toolbar.setContextMenuPolicy(Qt.PreventContextMenu)
        toolbar.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        toolbar.setOrientation(Qt.Horizontal)
        toolbar.setFloatable(True)
        toolbar.toggleViewAction().setChecked(True)
        toolbar.toggleViewAction().trigger()
        if isinstance(widget, list):
            for wig in widget:
                toolbar.addWidget(wig)
        else:
            toolbar.addWidget(widget)
        toolbar.setAllowedAreas(Qt.LeftToolBarArea | Qt.RightToolBarArea)
        if side == 1:
            self.addToolBar(Qt.LeftToolBarArea, toolbar)
        else:
            self.addToolBar(Qt.RightToolBarArea, toolbar)
        return toolbar
