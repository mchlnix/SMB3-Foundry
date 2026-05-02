"""Top-level editor window for Foundry's ROM and level workflow.

This module owns the application shell that coordinates ROM open or save,
level attachment, autosave, hot reload, tool windows, and the main editing
surface. It is the GUI entry point where model loading, persistent settings,
and editor commands meet the user-facing workflow.

See Also
--------
foundry.gui.MainWindow
    Base window behavior shared across Foundry's top-level UI.
foundry.game.level.Level
    Core in-level model loaded, attached, and saved through this window.
foundry.gui.visualization.level.LevelView
    Primary level-editing surface hosted by the main window.
"""

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
    QLabel,
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
from foundry.gui.dialogs.JumpEditor import JumpEditor
from foundry.gui.dialogs.level_selector.LevelSelector import LevelSelector
from foundry.gui.dialogs.LevelHeaderEditor import LevelHeaderEditor
from foundry.gui.dialogs.LevelParseProgressDialog import LevelParseProgressDialog
from foundry.gui.dialogs.new_level_dialog import NewLevelDialog
from foundry.gui.dialogs.PaletteViewer import SidePalette
from foundry.gui.dialogs.SettingsDialog import POWERUPS, SettingsDialog
from foundry.gui.JumpList import JumpList
from foundry.gui.level_settings.level_settings_dialog import LevelSettingsDialog
from foundry.gui.localization import set_application_language, tr, tr_data_name
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
from smb3parse.constants import OBJECT_SET_NAMES, Constants
from smb3parse.data_points import Position
from smb3parse.levels import HEADER_LENGTH

TOOLBAR_ICON_SIZE = QSize(20, 20)
TR_CONTEXT = "FoundryMainWindow"
TR_KEY_CONTEXT = "foundry.main"
MAIN_LABELS = {
    "action.add_jump": "Add Jump",
    "action.close_level": "Close Level",
    "action.edit_header": "Level Header",
    "action.edit_level_settings": "Other Level Settings",
    "action.go_to_jump_destination": "Go to Jump Destination",
    "action.new_empty_level": "New Empty Level",
    "action.place_level_on_map": "Place Level on Map",
    "action.reload_level": "Reload Level",
    "action.select_new_level": "Select New Level",
    "action.set_jump_destination": "Set Jump Destination",
    "action.test_level": "Test Level",
    "action.warning_panel": "Warning Panel",
    "action.zoom_in": "Zoom In",
    "action.zoom_out": "Zoom Out",
    "level_name.new_object_set": "New {object_set} Level",
    "level_name.object_set": "{object_set} Level",
    "menu.level": "&Level",
    "toolbar.level_info": "Level Info Toolbar",
    "toolbar.menu": "Menu Toolbar",
    "toolbar.object": "Object Toolbar",
    "whats_this.edit_header": (
        "<b>Header Editor</b><br/>"
        "Many configurations regarding the level are done in its header, like the length of "
        "the timer, or where and how Mario enters the level.<br/>"
    ),
    "whats_this.go_to_jump_destination": "Opens the level, that can be reached from this one, e.g. by entering a pipe.",
    "whats_this.test_level": "Opens an emulator with the current Level set to 1-1.\nSee Settings.",
    "whats_this.warning_panel": "Shows a list of warnings.",
}


def _main_text(key: str) -> str:
    """Resolve a main-window UI string from a stable catalog key.

    FoundryMainWindow uses these labels when constructing menus and when
    replaying live language changes across open editor surfaces.

    Parameters
    ----------
    key : str
        Code-facing key inside ``MAIN_LABELS`` and the ``foundry.main`` catalog
        context.

    Returns
    -------
    str
        Localized display text for menus, actions, or help text. The result is
        display-only and is never used as ROM data, settings identity, undo
        payload, or command lookup key.
    """
    return tr(TR_KEY_CONTEXT, key, MAIN_LABELS[key])


class FoundryMainWindow(RomWatcherMixin, RomHotSwapMixin, MainWindow):
    """Coordinate Foundry's ROM-backed editing workflow.

    The main window is the application shell that joins the ROM singleton,
    ``LevelRef``, level canvas, object palettes, menus, jump editor, save flow,
    autosave files, and undo stack. It keeps user actions routed through
    commands where possible so edits can be undone, exported for debugging, and
    replayed after ROM reload or hot swap. It also owns the staging boundaries
    where unmanaged M3L data is attached to ROM addresses, palette edits are
    saved or discarded, and temporary instaplay ROMs are prepared for emulator
    launch.

    Attributes
    ----------
    _protect_undo_stack : bool
        Whether level-change handlers should preserve the undo stack.
    _rom_menu : RomMenu
        ROM inspection menu and its child viewer windows.
    add_jump_button : QPushButton
        Button that asks the jump workflow to add a jump to the active level.
    close_level_action : QAction
        Menu action that closes the active level without closing the ROM.
    context_menu : LevelContextMenu
        Shared context menu for level objects, enemies, and list selections.
    debug_menu : DebugMenu | None
        Optional debug menu for macro export, inspection, and nightly tooling.
    delete_shortcut : QShortcut
        Shortcut that routes delete requests to the focused editor widget.
    edit_header_action : QAction
        Menu action that opens the level header editor.
    edit_level_settings_action : QAction
        Menu action that opens the non-header level settings dialog.
    enemy_size_bar : EnemySizeBar
        Status widget showing enemy/item bank usage for the active level.
    file_menu : FileMenu
        File menu that owns ROM, M3L, ASM, FNS, and settings actions.
    help_menu : HelpMenu
        Help/About menu whose actions participate in live language refresh.
    jump_destination_action : QAction
        Action that opens or navigates to the selected jump destination.
    jump_list : JumpList
        List widget for editing the level's separate SMB3 jump table.
    level_menu : QMenu
        Menu containing level-editing, testing, and level-management actions.
    level_size_bar : LevelSizeBar
        Status widget showing level-object bank usage for the active level.
    level_toolbar : QToolBar
        Toolbar exposing common level-editing and zoom actions.
    level_view : LevelView
        Canvas that displays and edits the active level.
    menu_toolbar : QToolBar
        Toolbar that mirrors key menu actions for faster access.
    new_level_action : QAction
        Menu action that creates a detached empty level.
    object_dropdown : ObjectDropdown
        Compact selector synchronized with the object toolbar.
    object_list : ObjectList
        List view synchronized with level selection and ROM draw order.
    object_toolbar : ObjectToolBar
        Toolbox and recent-object UI for placing SMB3 objects and enemies.
    place_level_action : QAction
        Menu action that places or reattaches the active level on a world map.
    redo_action : QAction
        Undo-stack redo action.
    reload_action : QAction
        Menu action that reparses the active level from ROM data.
    scroll_panel : QScrollArea
        Scroll container that hosts the level canvas.
    select_level_action : QAction
        Menu action that opens the level selector.
    set_jump_destination_button : QPushButton
        Button that opens the jump-destination workflow for the selected jump.
    settings : Settings
        Persistent editor settings.
    spinner_panel : SpinnerPanel
        Property panel for nudging, resizing, and changing selected objects.
    status_bar : ObjectStatusBar
        Status bar that reports cursor, object, and selection state.
    test_level_action : QAction
        Action that launches the configured emulator against a temporary ROM.
    undo_action : QAction
        Undo-stack undo action.
    undo_stack : QUndoStack
        Command stack for reversible level and ROM-editing actions.
    view_menu : ViewMenu
        Menu for zoom and visualization toggles tied to ``LevelView``.
    warning_action : QAction
        Toolbar action that opens the warning panel and reflects warning state.
    warning_list : WarningList
        Panel that surfaces parse and level-integrity warnings for the active level.
    zoom_in_action : QAction
        Action that increases the level-view zoom.
    zoom_label : QLabel
        Toolbar label showing the active zoom factor.
    zoom_out_action : QAction
        Action that decreases the level-view zoom.
    """

    def __init__(self):
        """Build the main window and connect editor actions.

        Initialization wires settings, menus, toolbars, the level canvas,
        object selectors, jump controls, status panels, and update checks around
        a shared ``LevelRef`` and undo stack. This is where Foundry's top-level
        workflow is staged: ROM loading, level switching, undoable editing,
        autosave, viewer windows, and save/reload actions are all connected here
        before later methods drive individual user actions.
        """
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

        self.level_menu = QMenu(_main_text("menu.level"))

        self.undo_action = self.undo_stack.createUndoAction(self)
        self.undo_action.setIcon(icon("rotate-ccw.svg"))
        self.level_menu.addAction(self.undo_action)

        self.redo_action = self.undo_stack.createRedoAction(self)
        self.redo_action.setIcon(icon("rotate-cw.svg"))
        self.level_menu.addAction(self.redo_action)

        self.level_menu.addSeparator()

        self.new_level_action = self.level_menu.addAction(_main_text("action.new_empty_level"))
        self.new_level_action.setIcon(icon("file.svg"))
        self.new_level_action.triggered.connect(self.on_new_level)

        self.select_level_action = self.level_menu.addAction(_main_text("action.select_new_level"))
        self.select_level_action.setIcon(icon("globe.svg"))
        self.select_level_action.triggered.connect(self.open_level_selector)

        self.level_menu.addSeparator()

        self.test_level_action = self.level_menu.addAction(icon("play-circle.svg"), _main_text("action.test_level"))
        self.test_level_action.triggered.connect(self.on_play)
        self.test_level_action.setWhatsThis(_main_text("whats_this.test_level"))

        self.level_menu.addSeparator()

        self.place_level_action = self.level_menu.addAction(_main_text("action.place_level_on_map"))
        self.place_level_action.setIcon(icon("map-pin.svg"))
        self.place_level_action.triggered.connect(self.on_place_level)

        self.reload_action = self.level_menu.addAction(_main_text("action.reload_level"))
        self.reload_action.setIcon(icon("refresh-cw.svg"))
        self.reload_action.triggered.connect(self.reload_level)

        self.level_menu.addSeparator()

        self.edit_header_action = self.level_menu.addAction(_main_text("action.edit_header"))
        self.edit_header_action.setIcon(icon("tool.svg"))
        self.edit_header_action.triggered.connect(self.on_header_editor)

        self.edit_level_settings_action = self.level_menu.addAction(_main_text("action.edit_level_settings"))
        self.edit_level_settings_action.setIcon(icon("settings.svg"))
        self.edit_level_settings_action.triggered.connect(self.on_edit_level_settings)

        self.level_menu.addSeparator()

        self.close_level_action = self.level_menu.addAction(_main_text("action.close_level"))
        self.close_level_action.setIcon(icon("x.svg"))
        self.close_level_action.triggered.connect(self.close_current_level)

        self.menuBar().addMenu(self.level_menu)

        self._rom_menu = RomMenu(self.level_ref)
        self._rom_menu.needs_gui_refresh.connect(self.enable_disable_gui_elements)
        self.menuBar().addMenu(self._rom_menu)

        self.context_menu = LevelContextMenu(self.level_ref)
        self.context_menu.triggered.connect(self.on_menu)

        self.level_view = LevelView(self, self.level_ref, self.settings, self.context_menu)

        self.view_menu = ViewMenu(self.level_view)

        self.menuBar().addMenu(self.view_menu)

        self.help_menu = HelpMenu(self)
        self.menuBar().addMenu(self.help_menu)

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

        self.add_jump_button = QPushButton(_main_text("action.add_jump"))
        self.add_jump_button.clicked.connect(self.on_jump_added)

        self.set_jump_destination_button = QPushButton(_main_text("action.set_jump_destination"))
        self.set_jump_destination_button.clicked.connect(self._show_jump_dest)

        jump_buttons.layout().addWidget(self.add_jump_button)
        jump_buttons.layout().addWidget(self.set_jump_destination_button)

        splitter = QSplitter(self)
        splitter.setOrientation(Qt.Orientation.Vertical)

        splitter.addWidget(self.object_list)
        splitter.setStretchFactor(0, 1)
        splitter.addWidget(self.jump_list)
        splitter.addWidget(jump_buttons)

        splitter.setChildrenCollapsible(False)

        self.level_toolbar = QToolBar(_main_text("toolbar.level_info"), self)
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

        object_toolbar = QToolBar(_main_text("toolbar.object"), self)
        object_toolbar.setContextMenuPolicy(Qt.ContextMenuPolicy.PreventContextMenu)
        object_toolbar.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        object_toolbar.setFloatable(False)

        object_toolbar.addWidget(self.object_toolbar)
        object_toolbar.setAllowedAreas(Qt.ToolBarArea.LeftToolBarArea | Qt.ToolBarArea.RightToolBarArea)

        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, object_toolbar)

        self.menu_toolbar = QToolBar(_main_text("toolbar.menu"), self)
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

        self.menu_toolbar.addAction(self.test_level_action)

        self.menu_toolbar.addSeparator()

        self.zoom_out_action = self.menu_toolbar.addAction(icon("zoom-out.svg"), _main_text("action.zoom_out"))
        self.zoom_out_action.triggered.connect(self.level_view.zoom_out)

        self.zoom_label = QLabel("0.00x")
        # make sure the label doesn't change sizes, when the label changes, causing the toolbar buttons to move around
        self.zoom_label.setMinimumSize(self.zoom_label.sizeHint())

        self.zoom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.menu_toolbar.addWidget(self.zoom_label)

        self.zoom_in_action = self.menu_toolbar.addAction(icon("zoom-in.svg"), _main_text("action.zoom_in"))
        self.zoom_in_action.triggered.connect(self.level_view.zoom_in)

        self.menu_toolbar.addSeparator()

        self.menu_toolbar.addAction(self.edit_header_action)
        self.edit_header_action.setWhatsThis(_main_text("whats_this.edit_header"))

        self.menu_toolbar.addAction(self.edit_level_settings_action)

        self.jump_destination_action = self.menu_toolbar.addAction(
            icon("arrow-right-circle.svg"), _main_text("action.go_to_jump_destination")
        )
        self.jump_destination_action.triggered.connect(self._go_to_jump_destination)
        self.jump_destination_action.setWhatsThis(_main_text("whats_this.go_to_jump_destination"))

        self.menu_toolbar.addSeparator()

        self.menu_toolbar.addAction(self.help_menu.whats_this_action)

        self.menu_toolbar.addSeparator()
        self.warning_list = WarningList(self, self.level_ref, self.level_view, self.object_list)

        self.warning_action = self.menu_toolbar.addAction(
            icon("alert-triangle.svg"), _main_text("action.warning_panel")
        )
        self.warning_action.setWhatsThis(_main_text("whats_this.warning_panel"))
        self.warning_action.triggered.connect(self.warning_list.show)
        self.warning_action.setDisabled(True)

        self.warning_list.warnings_updated.connect(self.warning_action.setEnabled)

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
            [
                Qt.Modifier.CTRL | Qt.Key.Key_Y,
                Qt.Modifier.CTRL | Qt.Modifier.SHIFT | Qt.Key.Key_Z,
            ]
        )

        QShortcut(
            QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_Plus),
            self,
            self.level_view.zoom_in,
        )
        QShortcut(
            QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_Minus),
            self,
            self.level_view.zoom_out,
        )

        QShortcut(
            QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_A),
            self,
            self.level_view.select_all,
        )
        QShortcut(
            QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_L),
            self,
            self.object_dropdown.setFocus,
        )

        self.rom_content_changed.connect(self._on_rom_changed_externally)

        self.check_for_update_on_startup()

        self.level_view.set_zoom(self.settings.value("level_view/last_zoom_factor"))

        self.showMaximized()

    def _add_debug_menu(self):
        """Create the debug menu once when debug mode is enabled."""
        if self.debug_menu:
            return

        self.debug_menu = DebugMenu(self)
        self.menuBar().addMenu(self.debug_menu)

    def on_new_level(self, dont_check=False):
        """Create a detached empty level from the new-level dialog.

        New levels start outside the ROM with zero object and enemy addresses.
        They use the selected object set and a minimal SMB3 level header until
        the save flow asks the user where to attach the level in ROM memory.

        Parameters
        ----------
        dont_check : bool, optional
            Whether to skip unsaved-change and palette prompts.
        """
        if not dont_check and not self.safe_to_change():
            return

        new_level_dialog = NewLevelDialog(self)
        if new_level_dialog.exec() == QDialog.DialogCode.Rejected:
            return

        object_set = new_level_dialog.object_set_index

        self._reload_rom()

        self.level_ref.level = Level(
            _main_text("level_name.new_object_set").format(
                object_set=tr_data_name("ObjectSet", OBJECT_SET_NAMES[object_set])
            ),
            object_set_number=object_set,
            world_number=1,
        )

        minimal_level_header = bytearray([0, 0, 0, 0, 0, 0, 0x81, object_set, 0])
        self.level_ref.level.from_bytes(object_data=(0, minimal_level_header), enemy_data=(0, bytearray()))

        self.level_ref.level_changed.emit()

    def _reload_rom(self):
        """Reload the ROM file into the shared ROM singleton.

        Missing ROM files are reported through the main-window error dialog and
        then re-raised so higher-level workflows such as reload, hot swap, open,
        or instaplay can stop without continuing on stale ROM state.

        Raises
        ------
        Exception
            If Exception is raised by the underlying operation.
        """
        try:
            ROM.reload_from_file()
        except FileNotFoundError:
            self._on_rom_not_found(ROM.path)
            raise

    def _on_rom_not_found(self, path: str):
        """Show the missing-ROM error dialog.


        Parameters
        ----------
        path : str
            ROM path that could not be read.
        """
        QMessageBox.critical(
            self,
            tr(TR_CONTEXT, "rom_not_found", "ROM not found"),
            tr(
                TR_CONTEXT,
                "error.rom_path_missing",
                "Could not find ROM at '{path}'.\n\nIt was either deleted or never existed in the first place.",
            ).format(path=path),
        )

    def _on_level_data_changed(self):
        """Refresh save state and autosave data after a level edit.

        The save action is enabled when the level is detached from the ROM,
        undoable edits exist, or palette data changed. The method also refreshes
        object graphics for palette/object-set changes and stores recoverable
        level bytes for crash recovery.
        """
        level_is_not_attached = self.level_ref.level and not self.level_ref.level.attached_to_rom
        changes_were_made = not self.undo_stack.isClean() or PaletteGroup.changed

        if self.level_ref:
            self._update_block_graphics_in_ui()

        self.file_menu.save_rom_action.setEnabled(level_is_not_attached or changes_were_made)

        self.jump_destination_action.setEnabled(bool(self.level_ref.level and self.level_ref.level.has_next_area))

        self._save_auto_data()

    def _on_show_settings(self):
        """Open the editor settings dialog and refresh the level view if needed."""
        settings_dialog = SettingsDialog(self.settings, self)

        settings_dialog.needs_level_update.connect(self.level_view.update)
        settings_dialog.language_changed.connect(self._on_language_changed)

        settings_dialog.exec()

    def _on_language_changed(self, language_code: str) -> None:
        """Apply a settings language change through the app-wide refresh path.

        When a QApplication exists, the localization layer installs the
        selected catalog and recursively calls ``retranslate_ui`` on open
        widgets. The direct call is only the non-application fallback.

        Parameters
        ----------
        language_code : str
            Stable locale code selected in settings. Display names are never
            persisted or used to select catalogs.
        """
        app = QApplication.instance()
        if app is not None:
            set_application_language(app, language_code)
        else:
            self.retranslate_ui()

    def retranslate_ui(self) -> None:
        """Refresh open main-window surfaces after the translator changes.

        The main window is the top-level live-refresh boundary for Foundry. It
        rewrites menus, toolbars, jump controls, object selectors, warnings,
        status/footer widgets, and child panels in place while preserving the
        selected ``LevelRef``, ROM addresses, settings keys, undo commands,
        and ``Qt.UserRole`` object payloads. The refresh order follows the
        visible shell layout: menus first, then toolbar actions, then child
        panels that own their own live-refresh hooks.
        """
        self.file_menu.retranslate_ui()
        self.level_menu.setTitle(_main_text("menu.level"))
        self.new_level_action.setText(_main_text("action.new_empty_level"))
        self.select_level_action.setText(_main_text("action.select_new_level"))
        self.test_level_action.setText(_main_text("action.test_level"))
        self.test_level_action.setWhatsThis(_main_text("whats_this.test_level"))
        self.place_level_action.setText(_main_text("action.place_level_on_map"))
        self.reload_action.setText(_main_text("action.reload_level"))
        self.edit_header_action.setText(_main_text("action.edit_header"))
        self.edit_header_action.setWhatsThis(_main_text("whats_this.edit_header"))
        self.edit_level_settings_action.setText(_main_text("action.edit_level_settings"))
        self.close_level_action.setText(_main_text("action.close_level"))
        self.add_jump_button.setText(_main_text("action.add_jump"))
        self.set_jump_destination_button.setText(_main_text("action.set_jump_destination"))
        self.zoom_out_action.setText(_main_text("action.zoom_out"))
        self.zoom_in_action.setText(_main_text("action.zoom_in"))
        self.jump_destination_action.setText(_main_text("action.go_to_jump_destination"))
        self.jump_destination_action.setWhatsThis(_main_text("whats_this.go_to_jump_destination"))
        self.warning_action.setText(_main_text("action.warning_panel"))
        self.warning_action.setWhatsThis(_main_text("whats_this.warning_panel"))
        self._rom_menu.retranslate_ui()
        self.view_menu.retranslate_ui()
        self.help_menu.retranslate_ui()
        if self.debug_menu is not None:
            self.debug_menu.retranslate_ui()
        self.context_menu.retranslate_ui()
        self.object_dropdown.retranslate_ui()
        self.object_list.retranslate_ui()
        self.level_view.retranslate_ui()
        self.spinner_panel.retranslate_ui()
        self.jump_list.retranslate_ui()
        self.level_size_bar.retranslate_ui()
        self.enemy_size_bar.retranslate_ui()
        self.object_toolbar.retranslate_ui()
        self.status_bar.retranslate_ui()
        self.update_title()

    def _on_want_to_reload_rom(self):
        """Hot-swap the ROM after an explicit reload request."""
        self.hotswap_roms()
        self._update_accepted_hash()

    def hotswap_roms(self):
        """Reload the ROM while preserving the undo stack.

        The inherited hot-swap workflow changes the active level, which would
        normally clear undo history. ``_protect_undo_stack`` suppresses that
        cleanup while the ROM is reloaded and command history is replayed.
        """
        self._protect_undo_stack = True

        super().hotswap_roms()

        self._update_block_graphics_in_ui()

        self._protect_undo_stack = False

    def _on_rom_changed_externally(self):
        # need to disable it here to not run into multiple triggers of this
        """Prompt for hot swap when the watched ROM changes on disk.

        External changes are usually produced by Scribe or a build step. The
        user can reload the ROM and ask Foundry to replay current edits, or
        ignore the external changes and risk overwriting them on the next save.
        """
        with self._rom_watcher_disabled():
            wants_to_reload_rom = (
                self.settings.value("editor/monitor_rom_for_changes")
                and QMessageBox.information(
                    self,
                    tr(TR_CONTEXT, "rom_changed", "ROM Changed"),
                    tr(
                        TR_CONTEXT,
                        "warning.rom_external_change",
                        "The ROM has been changed externally.\n\nYou can have Foundry open the new ROM and try to apply your current changes to it. Or you can ignore the external changes.\n\nNote that those changes will be lost, if you save in Foundry afterwards.",
                    ),
                    QMessageBox.StandardButton.Ignore | QMessageBox.StandardButton.Apply,
                )
                == QMessageBox.StandardButton.Apply
            )

            if wants_to_reload_rom:
                self.hotswap_roms()

            self._update_accepted_hash()

    @staticmethod
    def _save_auto_rom():
        """Write a temporary ROM copy used for crash recovery."""
        ROM.save_to_file(auto_save_rom_path, set_new_path=False)

    def _save_auto_data(self):
        """Write recoverable level bytes beside the autosave ROM.

        The autosave data stores object bytes, enemy bytes, their ROM addresses,
        and object set as JSON with base64 payloads so a future startup can
        reconstruct the edited level even if the main ROM file was not saved.
        """
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
        """Recover the previously autosaved level.

        Detached M3L edits are recovered from the autosaved M3L file. Attached
        ROM levels are reopened by address and then overwritten with the stored
        object and enemy bytes.
        """
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
                    tr(TR_CONTEXT, "failed_loading_auto_save", "Failed loading auto save"),
                    tr(
                        TR_CONTEXT,
                        "error.m3l_recovery_failed",
                        "Could not recover m3l file, that was edited, when the editor crashed.",
                    ),
                )

            self.load_m3l(auto_save_m3l_path)
        else:
            self.update_level("recovered level", object_address, enemy_address, object_set_number)
            self.level_ref.level.from_bytes((object_address, object_data), (enemy_address, enemy_data), True)

    def _go_to_jump_destination(self):
        """Open the level referenced by the next-area header fields.

        The open level is reloaded from ROM before switching. If the target
        address is not found in the world/level lookup, the existing world number
        is kept for display and later save behavior so detached or custom
        destination data still remains usable in the editor.
        """
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

        self.update_level(
            f"Level {world}-{level}",
            level_address,
            enemy_address,
            object_set,
            new_world,
        )

    def on_play(self, temp_dir=Path()):
        """Launch instaplay against a temporary ROM copy.

        The provided ``temp_dir`` argument is ignored in favor of Foundry's
        standard temporary directory. The actual ROM patching happens later in
        ``_save_changes_to_instaplay_rom``, where the open level is staged as
        a temporary level 1-1 replacement before the base window launches the
        emulator.

        Parameters
        ----------
        temp_dir : Path, optional
            Ignored caller-provided temporary directory.
        """
        temp_dir = Path(tempfile.gettempdir()) / "smb3foundry"
        temp_dir.mkdir(parents=True, exist_ok=True)

        super(FoundryMainWindow, self).on_play(temp_dir)

    def _save_changes_to_instaplay_rom(self, path_to_temp_rom) -> bool:
        """Patch a temporary ROM with the active level for instaplay.

        The temporary ROM is patched with the active level, configured startup
        power-up, optional title-screen skips, and current palette data before
        it is handed to the emulator launcher.

        Parameters
        ----------
        path_to_temp_rom : Path
            Path to the temporary ROM used for instaplay.

        Returns
        -------
        bool
            True when the temporary ROM was patched and saved.
        """
        temp_rom = ROM.from_file(path_to_temp_rom)

        insta_player = InstaPlayer(temp_rom)

        try:
            insta_player.put_current_level_to_level_1_1(self.level_ref.level)

        except CantFindFirstTile as e:
            title = tr(TR_CONTEXT, "couldn_t_place_level", "Couldn't place level")
            message = tr(
                TR_CONTEXT,
                "error.world_level_tile_missing",
                "Could not find a level 1 tile in World {world} to put your level at.",
            ).format(world=e.world)

            QMessageBox.critical(self, title, message)

            return False

        except LevelNotAttached:
            title = tr(TR_CONTEXT, "couldn_t_place_level", "Couldn't place level")
            message = tr(
                TR_CONTEXT,
                "error.level_not_in_rom",
                "The Level is not part of the rom yet (M3L?). Try saving it into the ROM first.",
            )

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
        """Open the level header editor on the jump-destination tab."""
        header_editor = LevelHeaderEditor(self, self.level_ref)
        header_editor.tab_widget.setCurrentIndex(3)

        header_editor.exec()

    def update_title(self):
        """Update the window title from level, ROM, and version state.

        Nightly builds display their full nightly name. Stable releases are
        prefixed with ``v`` to match release tags.
        """
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
                level_name = _main_text("level_name.object_set").format(
                    object_set=tr_data_name("ObjectSet", OBJECT_SET_NAMES[self.level_ref.object_set_number])
                )

            level_name += " — "

        self.setWindowTitle(level_name + rom_name + f"{app_name} {version_name}")

    def update(self):
        """Refresh the zoom label before delegating to Qt repaint logic.

        The level canvas owns the actual zoom value, but the main window keeps
        the status label synchronized here so repaint requests, toolbar state,
        and zoom-display updates stay on the same UI path.

        Returns
        -------
        object
            Result returned by Qt's update path, if any.
        """
        self.zoom_label.setText(f"{self.level_view.zoom}x")
        return super().update()

    def on_open_rom(
        self,
        path_to_rom=Path(),
        check_for_asm_files=True,
        close_current_level=True,
        try_opening_level=True,
    ):
        """Open a ROM and stage the editor around its data.

        The workflow protects unsaved edits, loads the ROM singleton, starts the
        file watcher for external changes, optionally imports companion ASM/FNS
        metadata, refreshes global ROM-derived data, writes autosave state, and
        opens either a selected level or a new empty level. Auto-save ROMs are
        deliberately not watched because they are owned by Foundry. This is the
        top-level ingest path that turns a chosen ROM file into editor state.

        Parameters
        ----------
        path_to_rom : Path, optional
            Path to the ROM file.
        check_for_asm_files : bool, optional
            Whether related assembly files should be detected.
        close_current_level : bool, optional
            Whether the open level should be closed first.
        try_opening_level : bool, optional
            Whether the initial level should be opened after loading.
        """
        if not self.safe_to_change():
            return

        if not path_to_rom.is_file() and not (path_to_rom := self._ask_for_path_to_rom()).is_file():
            self.enable_disable_gui_elements()

            return

        # Proceed to load the file chosen by the user
        try:
            ROM.load_from_file(path_to_rom, reset_globals=False)
            if path_to_rom != auto_save_rom_path:
                self.set_rom_path_to_watch(path_to_rom)

            if close_current_level:
                self.close_current_level()

            with self._rom_watcher_disabled():
                if check_for_asm_files:
                    self._check_for_asm_fns_imports(path_to_rom)

                if self.settings.value("editor/ask_for_level_management"):
                    self._ask_for_level_management()

                self._check_for_refresh()

                self._update_accepted_hash()

        except FileNotFoundError:
            self._on_rom_not_found(path_to_rom)
            return

        except IOError as exp:
            QMessageBox.warning(
                self,
                type(exp).__name__,
                tr(TR_CONTEXT, "cannot_open_file_path_to_rom", "Cannot open file '{path_to_rom}'.").format(
                    path_to_rom=path_to_rom
                ),
            )
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
        """Import companion ASM/FNS data when the ROM needs it.

        Foundry reads several drawing and lookup tables from known vanilla ROM
        locations. If those bytes differ, or if matching ASM/FNS files sit next
        to the ROM, this method follows the user's loading preference and either
        imports the symbol metadata, prompts, or leaves global data untouched.
        It is the compatibility gate between stock-address assumptions and
        custom-build symbol data during ROM-open and ROM-reload workflows.

        Parameters
        ----------
        path_to_rom : str | Path
            Path to the ROM file.
        """
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
                tr(TR_CONTEXT, "incompatibilities_found", "Incompatibilities found"),
                tr(
                    TR_CONTEXT,
                    "prompt.import_asm_for_rom_mismatch",
                    "The data in your ROM differs from expected values. This is likely due to code changes.\n\nIf you compiled your own ROM, supplying additional ASM files can solve this issue. Do you want to import them now?",
                ),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            query_paths = answer == QMessageBox.StandardButton.Yes

        elif ask_found:
            answer = QMessageBox.question(
                self,
                tr(TR_CONTEXT, "asm_files_found", "ASM files found"),
                tr(
                    TR_CONTEXT,
                    "prompt.load_detected_asm_files",
                    "There were files in your ROM directory, that look like ASM files.\n\nIf you compiled your own ROM, perhaps you want to load those into the editor as well?",
                ),
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
        """Detect ROM lookup tables that differ from Foundry's expectations.

        Foundry reads several important lookup tables directly from ROM for
        drawing, level discovery, and decode behavior. If those byte sequences
        no longer match the stock US ROM layout, the editor assumes code or
        tables were relocated and prompts for ASM/FNS symbol imports instead of
        trusting stale hard-coded addresses. ``on_open_rom`` uses this check to
        decide whether ASM/FNS import needs to become part of the ROM-load
        workflow.

        Returns
        -------
        bool
            ``True`` when one or more ROM byte ranges no longer match the stock
            lookup-table layout Foundry expects.
        """
        addresses_and_expected_data = (
            (
                Constants.COMPLETABLE_TILES_LIST,
                bytearray(b"P\xe8\xe6\xbd\xe0\x00\x01@A\x80"),
            ),
            (
                Constants.LAYOUT_LIST_OFFSET,
                bytearray(b"\xaa\xa5;\xa6\\\xa7\r\xa9.\xaa"),
            ),
            (
                Constants.LEVELS_IN_WORLD_LIST_OFFSET,
                bytearray(b"|\xb4f\xb5\x98\xb6\x8c\xb7|\xb8"),
            ),
            (
                Constants.LEVEL_BASE_OFFSET,
                bytearray(b"\xff\x00\x01\x02\x03\x04\x05\x06\x07\x08"),
            ),
            (
                Constants.LEVEL_ENEMY_LIST_OFFSET,
                bytearray(b"R\xb4\x08\xb50\xb6H\xb7(\xb8"),
            ),
            (
                Constants.LEVEL_X_POS_LISTS,
                bytearray(b"=\xb4\xd9\xb4\xfc\xb5&\xb7\xfe\xb7"),
            ),
            (
                Constants.LEVEL_Y_POS_LISTS,
                bytearray(b"(\xb4\xaa\xb4\xc8\xb5\x04\xb7\xd4\xb7"),
            ),
            (
                Constants.OFFSET_BY_OBJECT_SET_A000,
                bytearray(b"\x0b\x0f\x15\x10\x11\x13\x12\x12\x12\x14"),
            ),
            (
                Constants.OFFSET_BY_OBJECT_SET_C000,
                bytearray(b"\n\x0e\x0e\x0e\x0e\x0e\x0e\x0e\x0e\x0e"),
            ),
            (
                Constants.SPECIAL_ENTERABLE_TILES_LIST,
                bytearray(b"P\xe8\xbc\xe0\xc9_\xdff\xbd\xe6"),
            ),
            (
                Constants.STRUCTURE_DATA_OFFSETS,
                bytearray(b"$\xb4\xa6\xb4\xc4\xb5\x00\xb7\xd0\xb7"),
            ),
            (
                Constants.TILE_ATTRIBUTES_TS0_OFFSET,
                bytearray(b"\x03g\xbf\xe9\x03g\xbf\xe9 \x0e"),
            ),
            (
                Constants.TSA_OS_LIST,
                bytearray(b"\x0b\x0f\x15\x10\x11\x13\x12\x12\x12\x14"),
            ),
            (
                Constants.LEVEL_LOAD_ROUTINE_BY_OBJECT_SET,
                bytearray(b"\xad\n\x07 \x99\xfe\x08\xa4\x08\xa4"),
            ),
        )

        for address, expected_data in addresses_and_expected_data:
            if ROM().read(address, len(expected_data)) != expected_data:
                return True
        else:
            return False

    @staticmethod
    def _rom_has_asm_files_in_path(rom_path: Path):
        """Detect ASM and FNS files beside a ROM.

        Both files are needed for Foundry to import relocated code symbols from
        a custom build, so this helper feeds the ROM-open decision about
        whether assembly metadata can be loaded automatically. The result
        drives the ROM-open workflow before any import prompt is shown: callers
        use it to decide whether the editor can immediately offer ASM-backed
        symbol loading for the selected ROM or must stay on the vanilla ROM
        path without assembly metadata.

        Parameters
        ----------
        rom_path : Path
            Path to the rom file or directory.

        Returns
        -------
        bool
            True when matching assembly files exist beside the ROM.
        """
        containing_dir = rom_path.parent

        has_asm_file = bool(list(containing_dir.glob("*.asm")))
        has_fns_file = bool(list(containing_dir.glob("*.fns")))

        return has_asm_file and has_fns_file

    def _ask_for_path_to_rom(self):
        # otherwise, ask the user what new file to open
        """Prompt the user for a ROM path.

        The dialog starts in the configured default directory and filters for
        supported NES ROM files.

        Returns
        -------
        Path
            Path selected for the ROM file, if one was chosen.
        """
        path_to_rom, _ = QFileDialog.getOpenFileName(
            self,
            caption=tr(TR_CONTEXT, "open_rom", "Open ROM"),
            dir=self.settings.value("editor/default_dir_path"),
            filter=ROM_FILE_FILTER,
        )

        return Path(path_to_rom)

    def on_open_m3l(self, _):
        """Prompt for and load an external M3L level file.

        The ROM is reloaded first so the detached level starts from current ROM
        globals, then the M3L is loaded into ``LevelRef`` and copied to the
        autosave M3L path for crash recovery.

        Parameters
        ----------
        _ : object
            Unused Qt signal payload.
        """
        if not self.safe_to_change():
            return

        # otherwise, ask the user what new file to open
        if not (pathname := load_m3l_filename(self.settings.value("editor/default_dir_path"))):
            return

        self._reload_rom()

        self.load_m3l(pathname)
        save_m3l(auto_save_m3l_path, self.level_ref.level.to_m3l())

    def load_m3l(self, pathname: Path | str):
        """Load an external M3L level into the active editor state.

        M3L data can describe a level that is not attached to ROM addresses yet.
        The save flow later asks the user where to place its object and enemy
        streams before writing it back to a ROM.

        Parameters
        ----------
        pathname : Path | str
            Path to the M3L file to load.
        """
        if not self._ask_for_palette_save():
            return

        if self.level_ref.level is None:
            self.level_ref.level = Level()

        load_m3l(pathname, self.level_ref.level)

    def safe_to_change(self) -> bool:
        """Check whether the editor state can be replaced safely.

        This extends the base unsaved-change prompt with palette handling so ROM
        reloads, level switches, file opens, and crash-recovery flows do not
        silently discard palette edits that live outside the undo stack.

        Returns
        -------
        bool
            True when safe to change.
        """
        return super(FoundryMainWindow, self).safe_to_change() and self._ask_for_palette_save()

    def on_save_rom(self, _):
        """Save changes back to the loaded ROM path.

        Parameters
        ----------
        _ : object
            Unused Qt signal payload.
        """
        self.try_saving_rom(False)

    def on_save_rom_as(self, _):
        """Prompt for a path and save the ROM there.

        Parameters
        ----------
        _ : object
            Unused Qt signal payload.
        """
        self.try_saving_rom(True)

    def _ask_for_level_management(self):
        """Ask whether Foundry should manage level storage automatically.

        SMB3 stores levels of the same object set in shared ROM regions, so
        expanding one level can overwrite the next one. When enabled, Foundry
        parses reachable levels and rearranges object/enemy data to preserve
        spacing for edited levels.
        """
        if ROM.additional_data.managed_level_positions is not None:
            return

        answer = QMessageBox.question(
            NO_PARENT,
            tr(TR_CONTEXT, "automatic_level_management_feature", "Automatic Level Management Feature"),
            tr(
                TR_CONTEXT,
                "help.automatic_level_management",
                "Levels of the same type are stored in the same area of the ROM. If you add new objects to a Level, you might overwrite the Level, that comes right after it in memory.\n\nFoundry can parse your ROM and find all Levels accessible to the player (!). That way, when you extend a Level, Foundry can automatically move the Levels, so that this doesn't happen and so that you can use as much memory as is available for that type of Level.\n\nThis can also be (de-)activated under 'Rom Settings' later.",
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Ignore,
        )

        if answer == QMessageBox.StandardButton.Ignore:
            return

        if answer == QMessageBox.StandardButton.No:
            ROM.additional_data.managed_level_positions = False
            self.on_save_rom(None)

        if answer == QMessageBox.StandardButton.Yes:
            if not self._found_level_load_code():
                return

            ROM.additional_data.managed_level_positions = True
            self._parse_levels_in_rom()

    def _found_level_load_code(self):
        """Detect vanilla level-load code where parsing expects it.

        Automatic level management depends on known lookup tables and load code
        addresses. If the ROM has moved that code, Foundry warns instead of
        parsing with stale addresses, because the managed-level discovery pass
        would otherwise walk the wrong load routine. In workflow terms this is
        the gate between the user consenting to managed level placement and the
        expensive parse that rewrites reachable-level layout assumptions:
        success allows ``_parse_levels_in_rom()`` to proceed, while failure
        stops the feature before any managed-address state is enabled.

        Returns
        -------
        bool
            True when the expected level-load bytes are present and managed
            level parsing can safely continue.
        """
        expected_data = bytearray(b"\xad\n\x07 \x99\xfe\x08\xa4\x08\xa4")

        found_data = ROM().read(Constants.LEVEL_LOAD_ROUTINE_BY_OBJECT_SET, len(expected_data))

        if found_data != expected_data:
            QMessageBox.warning(
                self,
                tr(TR_CONTEXT, "automatic_level_management_feature", "Automatic Level Management Feature"),
                tr(
                    TR_CONTEXT,
                    "error.level_load_offset_changed",
                    "The ROM was changed in a way that makes this feature unavailable. LevelLoad_ByTileset was not where we expected it.",
                ),
            )

        return found_data == expected_data

    @staticmethod
    def _parse_levels_in_rom():
        """Parse reachable ROM levels and rearrange managed storage.

        The progress dialog discovers levels by address. The organizer then
        rearranges level and enemy data so managed levels have safe storage
        ranges before the ROM is saved.
        """
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
        """Scribe can move around levels, so we would need to read them in again.

        Foundry stores parsed level locations in additional ROM metadata. When
        another tool marks that metadata stale, this asks whether to reparse or
        clear the managed-level list and fall back to map-based level selection.
        """
        if not ROM.additional_data.needs_refresh:
            return

        answer = QMessageBox.question(
            self,
            tr(TR_CONTEXT, "external_changes_to_levels_detected", "External Changes to Levels detected"),
            tr(
                TR_CONTEXT,
                "prompt.reparse_moved_levels",
                "We detected changes to where Levels are saved from a different source (probably SMB3 Scribe). We need to parse the ROM again to update the locations of the moved Levels.\n\nIf you choose 'No', then the Found Level information will be deleted, but you can still select Levels through the world maps in the Level Selector, as before.\n\nReparse the Levels?",
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        ROM.additional_data.found_levels.clear()
        ROM.additional_data.needs_refresh = False

        ROM.additional_data.managed_level_positions = answer == QMessageBox.StandardButton.Yes

        if ROM.additional_data.managed_level_positions:
            self._parse_levels_in_rom()
        else:
            # save the clearing of the level data as well
            ROM.save_to_file(ROM.path)

    def _ask_for_palette_save(self) -> bool:
        """Ask how to handle unsaved object palette changes.

        This keeps palette-save prompting explicit before level switching, saving, or other actions
        that could discard palette edits.

        Returns
        -------
        bool
            False when the user cancels; otherwise true after palettes are saved or restored.
        """
        if not PaletteGroup.changed:
            return True

        answer = QMessageBox.question(
            self,
            tr(TR_CONTEXT, "please_confirm", "Please confirm"),
            tr(
                TR_CONTEXT,
                "prompt.save_palette_changes",
                "You changed some object palettes. This is a change, that potentially affects other levels in this ROM. Do you want to save these changes, or restore the defaults and continue?",
            ),
            QMessageBox.StandardButton.Cancel
            | QMessageBox.StandardButton.RestoreDefaults
            | QMessageBox.StandardButton.Save,
            QMessageBox.StandardButton.Cancel,
        )

        if answer == QMessageBox.StandardButton.Cancel:
            return False

        if answer == QMessageBox.StandardButton.Save:
            save_all_palette_groups()
            self._write_to_rom(ROM.path, False)

        elif answer == QMessageBox.StandardButton.RestoreDefaults:
            restore_all_palettes()
            self.level_ref.level.reload()

        return True

    def try_saving_rom(self, is_save_as):
        """Run the guarded ROM save workflow.

        Saving checks whether the open level is safe for the target ROM,
        attaches unmanaged M3L data to selected ROM addresses when needed,
        offers palette save/restore handling, prevents writing to the temporary
        autosave ROM, writes the ROM file, and marks the undo stack clean for a
        normal save. It is the main commit boundary between edited in-memory
        level state and persisted ROM bytes for the window workflow.

        Parameters
        ----------
        is_save_as : bool
            Whether the save operation should prompt for a target path.
        """
        safe_to_save, reason, additional_info = self.level_view.level_safe_to_save()

        if not safe_to_save:
            answer = QMessageBox.warning(
                self,
                reason,
                tr(
                    TR_CONTEXT, "additional_info_do_you_want_to_proceed", "{additional_info}\n\nDo you want to proceed?"
                ).format(additional_info=additional_info),
                QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes,
                QMessageBox.StandardButton.No,
            )

            if answer == QMessageBox.StandardButton.No:
                return

        if self.level_ref and not self.level_ref.attached_to_rom:
            QMessageBox.information(
                self,
                tr(TR_CONTEXT, "importing_m3l_into_rom", "Importing M3L into ROM"),
                tr(
                    TR_CONTEXT,
                    "prompt.import_m3l_offsets",
                    "You are currently editing a level stored in an m3l file outside of the ROM. Please select the positions in the ROM you want the level objects and enemies/items to be stored.",
                ),
                QMessageBox.StandardButton.Ok,
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
                caption=tr(TR_CONTEXT, "save_rom_as", "Save ROM as"),
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
                tr(TR_CONTEXT, "cannot_save_to_auto_save_rom", "Cannot save to auto save ROM"),
                tr(
                    TR_CONTEXT,
                    "error.cannot_save_auto_save_rom",
                    "You can't save to the auto save ROM, as it will be deleted, when exiting the editor. Please choose another location, or your changes will be lost.",
                ),
            )

            return

        if self._save_current_changes_to_file(pathname, set_new_path=True) and not is_save_as:
            with self._rom_watcher_disabled():
                self.undo_stack.setClean()

                # Make sure the rom file watcher goes off right now, so it ignores the change
                QApplication.processEvents()

        self.update_title()

    def on_import_enemies_from_asm(self):
        """Prompt for enemy ASM and import it through the undo stack.

        Enemy ASM import replaces the level's enemy bytes, so it is wrapped in
        an undo command instead of being applied as a direct file operation.
        """
        if not (
            pathname := load_asm_filename(
                tr(TR_CONTEXT, "enemy_asm", "Enemy ASM"),
                self.settings.value("editor/default_dir_path"),
            )
        ):
            return

        self.undo_stack.push(ImportASMEnemies(self.level_ref, pathname))

    def _attach_to_rom(self, object_data_offset: int, enemy_data_offset: int):
        """Attach the level to ROM object and enemy addresses.

        The attachment is represented as an undo command so importing an M3L
        into the ROM remains reversible until the save is committed. This is
        the staging step that turns detached data into a ROM-backed level.

        Parameters
        ----------
        object_data_offset : int
            ROM offset for object data.
        enemy_data_offset : int
            ROM offset for enemy data.

        Raises
        ------
        ValueError
            If the input data or current state is invalid.
        """
        if 0x0 in [object_data_offset, enemy_data_offset]:
            raise ValueError("You cannot save level or enemy data to the beginning of the ROM (address 0x0).")

        self.undo_stack.push(AttachLevelToRom(self.level_ref, object_data_offset, enemy_data_offset))

    def _save_current_changes_to_file(self, pathname: str, set_new_path: bool):
        """Save the active level and refresh the autosave ROM.

        The base save serializes the active level into the ROM and writes the
        target file. The autosave ROM is refreshed afterward even if the write
        raises, keeping recovery data aligned with the latest in-memory state.

        Parameters
        ----------
        pathname : str
            Destination ROM path.
        set_new_path : bool
            Whether ``pathname`` should become the active ROM path.

        Returns
        -------
        bool
            True when current changes were saved to disk.
        """
        try:
            return super(FoundryMainWindow, self)._save_current_changes_to_file(pathname, set_new_path)
        finally:
            self._save_auto_rom()

    def on_menu(self, action: QAction):
        """Route a level context-menu action to the matching editor command.

        The context menu is shared by the canvas and object list. This method
        maps its last global position back into level-view coordinates and then
        performs the selected object operation through undo commands where the
        operation mutates level data.

        Parameters
        ----------
        action : QAction
            Qt action connected to the menu behavior.
        """
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
        """Reload the open level from the loaded ROM path.

        The open level's identifying ROM addresses, object set, name, and
        world number are captured before reloading so the same level can be
        opened again from fresh persisted bytes rather than whatever the editor
        currently has in memory.
        """
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
        """Place or attach the open level through the world map selector.

        Managed ROM levels reuse their existing object and enemy addresses.
        External or detached levels first receive addresses selected by the
        level selector, then the chosen world-map pointer is written back with
        the level address, enemy address, and object set.

        Returns
        -------
        bool
            True when a world-map pointer was updated.
        """
        if not self.level_ref:
            return False

        level_selector = LevelSelector(self)
        level_selector.goto_world(self.level_ref.level.world)
        level_selector.deactivate_level_list()

        if level_selector.exec() != QMessageBox.DialogCode.Accepted:
            return False

        if (level_pointer := level_selector.clicked_level_pointer) is None:
            QMessageBox.warning(
                self,
                tr(TR_CONTEXT, "no_level_on_map_selected", "No Level on Map selected"),
                tr(
                    TR_CONTEXT,
                    "error.world_map_position_required",
                    "You need to click a position on a World Map. If the position you want to use is not clickable, you can save this level as an M3L, add/move a level pointer to that position in Scribe and try again.",
                ),
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
        """Synchronize object selection between toolbar and dropdown.

        The sender check prevents feedback loops when one selector updates the
        other.

        Parameters
        ----------
        level_object : InLevelObject
            Object or enemy selected for placement.
        """
        if self.sender() is not self.object_dropdown:
            self.object_dropdown.select_object(level_object)

        if self.sender() is not self.object_toolbar:
            self.object_toolbar.select_object(level_object)

    def bring_objects_to_foreground(self):
        """Move selected level objects ahead in draw/storage order.

        The command affects level objects, not the separate enemy/item stream.
        """
        self.undo_stack.push(ToForeground(self.level_ref, self.level_ref.selected_objects))

    def bring_objects_to_background(self):
        """Move selected level objects behind other level objects.

        The command affects level objects, not the separate enemy/item stream.
        """
        self.undo_stack.push(ToBackground(self.level_ref, self.level_ref.selected_objects))

    def add_object_at(self, q_point: QPoint, domain=0, obj_type=0):
        """Push an undo command that places a level object.

        The command captures the level coordinate so placement remains stable
        across later zoom changes.

        Parameters
        ----------
        q_point : QPoint
            Point in widget coordinates.
        domain : int, optional
            Object domain that determines how the object is interpreted.
        obj_type : int, optional
            Object type identifier to place.
        """
        self.undo_stack.push(AddLevelObjectAt(self.level_view, q_point, domain, obj_type))

    def add_enemy_at(self, q_point: QPoint, enemy_type=0x72):
        """Push an undo command that places an enemy or item.

        The command captures the level coordinate so placement remains stable
        across later zoom changes.

        Parameters
        ----------
        q_point : QPoint
            Point in widget coordinates.
        enemy_type : int, optional
            Enemy type identifier to place.
        """
        self.undo_stack.push(AddEnemyAt(self.level_view, q_point, enemy_type))

    def _cut_objects(self):
        """Copy selected objects and remove them from the level.

        Removal is routed through the undo stack, so cut can be undone.
        """
        self._copy_objects()
        self.remove_selected_objects()

    def _copy_objects(self):
        """Store the selected objects in the context-menu clipboard.

        The copied payload includes the objects and their reference point so
        paste can preserve relative layout at a new level coordinate and route
        the later insertion through undoable paste commands.
        """
        selected_objects = self.level_view.get_selected_objects().copy()

        if selected_objects:
            self.context_menu.set_copied_objects(selected_objects)

    def _paste_objects(self, q_point: QPoint | None = None):
        """Paste copied objects at a view position or the last mouse position.

        Existing selection is cleared before pushing the paste command so the
        newly pasted objects become the active selection.

        Parameters
        ----------
        q_point : QPoint | None, optional
            Point in widget coordinates.
        """
        if not (copied_objects := self.context_menu.get_copied_objects())[0]:
            return

        if q_point is None:
            q_point = self.level_view.from_level_point(*self.level_view.last_mouse_position.xy)

        copied_level_objects = cast(tuple[list[InLevelObject], Position], copied_objects)

        # clear selection of copied/other previously selected objects, so only the pasted ones are selected
        self.level_view.select_objects([], replace_selection=True)

        self.undo_stack.push(PasteObjectsAt(self.level_view, copied_level_objects, q_point))

    def _on_delete_key(self):
        # if the jump list is focused and a jump is selected, delete it
        """Delete the focused jump or selected level objects.

        Delete is routed to the jump list when that widget has focus; otherwise
        it removes selected canvas/list objects through the undo stack.
        """
        if self.focusWidget() is self.jump_list:
            self.jump_list.delete_selected_jump()

            return

        # otherwise simply delete selected objects in the level view
        self.remove_selected_objects()

    def remove_selected_objects(self):
        """Remove all selected level objects and enemies through undo."""
        selected_objects = [obj for obj in self.level_ref.level.get_all_objects() if obj.selected]

        if not selected_objects:
            return

        self.undo_stack.push(RemoveObjects(self.level_ref, selected_objects))

    def on_spin(self, _):
        """Replace the single selected object with spinner values.

        The spinner edits the selected object's SMB3 domain/type/length fields
        or the selected enemy's type. Repeated cycling is mergeable in the undo
        stack through the replacement commands.

        Parameters
        ----------
        _ : object
            Unused Qt signal payload.
        """
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
        """Open the level selector and load the chosen ROM level.

        When a ROM level is already active, the selector is prefilled with that
        level's world, object set, layout address, and enemy address. A chosen
        level reloads the ROM first so the editor opens fresh persisted bytes.

        Parameters
        ----------
        _ : object
            Unused Qt signal payload.

        Returns
        -------
        bool
            True when a level was selected and loaded.
        """
        if not self.safe_to_change():
            return False

        level_selector = LevelSelector(self)
        if self.level_ref and self.level_ref.level.attached_to_rom:
            level_selector.goto_world(self.level_ref.level.world)
            level_selector.fill_in_data(
                self.level_ref.level.object_set_number,
                self.level_ref.level.layout_address,
                self.level_ref.level.enemy_offset,
            )

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
        """Open the level settings dialog for the active level.

        Parameters
        ----------
        _ : object
            Unused Qt signal payload.
        """
        LevelSettingsDialog(self, self.level_ref).exec()

    def on_header_editor(self, _):
        """Open the SMB3 level header editor for the active level.

        Parameters
        ----------
        _ : object
            Unused Qt signal payload.
        """
        LevelHeaderEditor(self, self.level_ref).exec()

    def update_level(
        self,
        level_name: str,
        object_data_offset: LevelAddress,
        enemy_data_offset: EnemyItemAddress,
        object_set: int,
        world_number=-1,
    ):
        """Load a ROM level into ``LevelRef`` and remember it in settings.

        The zero-value guard prevents attempts to load invalid level metadata
        from corrupt or placeholder world-map entries. After a successful load,
        the canvas scroll position is reset and the level identity is stored so
        Foundry can reopen the same level on startup or after external ROM
        reload flows.

        Parameters
        ----------
        level_name : str
            Display name for the level.
        object_data_offset : LevelAddress
            ROM offset for object data.
        enemy_data_offset : EnemyItemAddress
            ROM offset for enemy data.
        object_set : int
            Object set that controls tiles, graphics, or level object behavior.
        world_number : int, optional
            One-based SMB3 world number being processed.
        """
        try:
            if 0 in (object_data_offset, enemy_data_offset, object_set, world_number):
                QMessageBox.critical(
                    self,
                    tr(TR_CONTEXT, "invalid_level_data", "Invalid Level Data"),
                    tr(
                        TR_CONTEXT,
                        "error.invalid_level_offsets",
                        "Given level data was not loadable.\n\nobject_data_offset={object_data_offset!r}\nenemy_data_offset={enemy_data_offset!r}\nobject_set={object_set!r}\nworld_number={world_number!r}",
                    ).format(
                        object_data_offset=object_data_offset,
                        enemy_data_offset=enemy_data_offset,
                        object_set=object_set,
                        world_number=world_number,
                    ),
                )
                return

            self.level_ref.load_level(
                level_name,
                object_data_offset,
                enemy_data_offset,
                object_set,
                world_number,
            )
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
                tr(TR_CONTEXT, "please_confirm", "Please confirm"),
                tr(TR_CONTEXT, "error.level_offset_mismatch", "Failed loading level. The level offsets don't match."),
            )

    def close_current_level(self):
        """Unload the active level and clear undo history when appropriate.

        ROM hot swap temporarily protects the undo stack because it closes and
        reopens the level as part of replaying current edits.
        """
        if not self.safe_to_change():
            return

        self.level_ref.level = None
        if not self._protect_undo_stack:
            self.undo_stack.clear()
        self.enable_disable_gui_elements()

    def update_gui_for_level(self):
        """Refresh editor widgets after the active level changes.

        This resets palettes, clears undo history unless a hot swap is in
        progress, updates title/status widgets, and switches object/jump editing
        controls off for world-map views so the same shell can host both level
        editing and overworld editing workflows.
        """
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
                self.level_ref.object_set_number,
                self.level_ref.graphic_set,
                self.level_ref.object_palette_index,
            )

            self.jump_list.setEnabled(True)

        self.level_view.update()

    def _update_block_graphics_in_ui(self):
        """Updates the representations of objects in the UI, in case the object set or graphics set changes.

        Object toolbar and dropdown icons depend on object set, graphics set,
        and object palette. Palette or header changes therefore need to refresh
        both selectors together.
        """
        if not self.level_ref:
            return

        self.object_toolbar.set_object_set(
            self.level_ref.object_set_number,
            self.level_ref.graphic_set,
            self.level_ref.object_palette_index,
        )
        self.object_dropdown.set_object_set(
            self.level_ref.object_set_number,
            self.level_ref.graphic_set,
            self.level_ref.object_palette_index,
        )

    def enable_disable_gui_elements(self):
        # actions and widgets that depend on whether the ROM is loaded
        """Enable actions based on ROM and level availability.

        ROM-level actions become available after a ROM is loaded. Level-editing
        actions require a fully loaded level, while undo/redo remain controlled
        by the undo stack itself. The method also refreshes save-state widgets
        that depend on current level size and attachment state.
        """
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
        """Open the jump editor for the selected jump."""
        index = self.jump_list.currentIndex().row()

        updated_jump = JumpEditor.edit_jump(self, self.level_view.level_ref.jumps[index])

        self.on_jump_edited(updated_jump)

    def on_jump_added(self):
        """Append a jump through the undo stack."""
        self.undo_stack.push(AddJump(self.level_ref))

    def on_jump_removed(self):
        """Remove the selected jump through the undo stack."""
        self.undo_stack.push(RemoveJump(self.level_ref, self.jump_list.currentIndex().row()))

    def on_jump_edited(self, new_jump: Jump):
        """Replace the selected jump with an edited jump.

        Jump edits are implemented as a macro of remove plus add so the change
        stays reversible and preserves the target list index.

        Parameters
        ----------
        new_jump : Jump
            Jump returned by the editor dialog.
        """
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

        self.jump_list.set_jump_text(index, new_jump)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Process main-window mouse shortcuts.

        Middle-click places the selected toolbar/dropdown object at the cursor
        when no drag is active. Back and forward mouse buttons map to undo and
        redo.

        Parameters
        ----------
        event : QMouseEvent
            Qt event delivered to the widget.
        """
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
        """Place the active toolbar or dropdown object.

        The dropdown and toolbar share selection state, so this method can use
        the dropdown payload, update recent objects, and route to the matching
        object or enemy placement command before notifying the level that its
        data changed. It is the shared placement path for toolbar, dropdown,
        and middle-click placement.

        Parameters
        ----------
        q_point : QPoint
            Point in widget coordinates.
        """
        in_level_object = self.object_dropdown.currentData(Qt.ItemDataRole.UserRole)

        self.object_toolbar.add_recent_object(in_level_object)

        if isinstance(in_level_object, LevelObject):
            self.add_object_at(q_point, in_level_object.domain, in_level_object.obj_index)
        elif isinstance(in_level_object, EnemyItem):
            self.add_enemy_at(q_point, in_level_object.obj_index)

        self.level_ref.level.data_changed.emit()

    def closeEvent(self, event: QCloseEvent):
        """Close child viewers and remove autosave files after exit approval.

        The base close handler may reject the event because of unsaved changes.
        Cleanup only runs after the event remains accepted.

        Parameters
        ----------
        event : QCloseEvent
            Qt event delivered to the widget.
        """
        super(FoundryMainWindow, self).closeEvent(event)

        if not event.isAccepted():
            return

        self._rom_menu.close_everything()

        auto_save_rom_path.unlink(missing_ok=True)
        auto_save_m3l_path.unlink(missing_ok=True)
        auto_save_level_data_path.unlink(missing_ok=True)
