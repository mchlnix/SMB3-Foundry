"""Coordinate the Scribe main window and its world-map editing workflow.

This module builds the top-level Qt window for SMB3 Scribe. It wires the ROM
loading flow inherited from :mod:`foundry.gui.MainWindow` to Scribe-specific
world-map editing surfaces such as :class:`scribe.gui.tool_window.tool_window.ToolWindow`,
the world view, clipboard-style object actions, and ASM export helpers.

The main window owns the user-facing workflow for opening a ROM, selecting a
world map, mutating tiles and map objects through the undo stack, saving back
to a ROM, and exporting the loaded map as the split ASM layout used
by SMB3 disassembly projects.

See Also
--------
foundry.gui.MainWindow.MainWindow
    Base editor window that provides ROM save, update, and instaplay support.
scribe.gui.tool_window.tool_window.ToolWindow
    Companion tool palette that chooses which map entity the world view edits.
foundry.gui.visualization.world.WorldView.WorldView
    Canvas that renders and edits the active world map.
"""

import sys
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
from foundry.gui.localization import set_application_language, tr
from foundry.gui.settings import Settings
from foundry.gui.visualization.world.WorldView import WorldView
from scribe.gui.commands import PutTile
from scribe.gui.menus.edit_menu import EditMenu
from scribe.gui.menus.help_menu import HelpMenu
from scribe.gui.menus.view_menu import ViewMenu
from scribe.gui.settings_dialog import SettingsDialog
from scribe.gui.tool_window.tool_window import ToolWindow
from scribe.gui.world_view_context_menu import WorldContextMenu
from smb3parse.constants import (
    MAPOBJ_ASM_SYMBOLS,
    STARTING_WORLD_INDEX_ADDRESS,
    WORLD_MAP_OBJECT_SET,
)
from smb3parse.data_points import Position
from smb3parse.levels import (
    MAX_SCREEN_COUNT,
    WORLD_COUNT,
    WORLD_MAP_BLANK_TILE_ID,
    WORLD_MAP_HEIGHT,
    WORLD_MAP_SCREEN_WIDTH,
)
from smb3parse.levels.world_map import WorldMap as SMB3WorldMap

TR_KEY_CONTEXT = "scribe.main"


def _tr(key: str) -> str:
    """Translate a Scribe main-window label by stable catalog key.

    Parameters
    ----------
    key : str
        Key within the ``scribe.main`` catalog context.

    Returns
    -------
    str
        Localized display text for menus, actions, toolbars, or window titles.

    Notes
    -----
    Main-window strings use semantic catalog keys so live retranslation can
    refresh visible labels without letting English prose become persisted
    settings, undo-command text identity, or ROM data.
    """
    return tr(TR_KEY_CONTEXT, key)


class ScribeMainWindow(MainWindow):
    """Own the Scribe editor shell for one loaded SMB3 ROM.

    The window coordinates three persistent collaborators: the shared
    :attr:`level_ref` model inherited from
    :class:`foundry.gui.MainWindow.MainWindow`, a
    :class:`PySide6.QtGui.QUndoStack` that gates destructive navigation and
    save-state UI, and the Scribe-specific views that edit the active world
    map. Menu actions, toolbar actions, keyboard shortcuts, and context-menu
    actions all funnel through this class so they update the same active map
    and undo history.

    Parameters
    ----------
    path_to_rom : str
        Startup ROM path. An empty string triggers the normal open-file dialog.

    Attributes
    ----------
    undo_stack : QUndoStack
        Undo history for tile, sprite, and world-map pointer edits.
    level_ref : foundry.game.level.LevelRef.LevelRef
        Shared level reference that swaps between loaded world maps and
        notifies the view, menus, and tool window when the active map changes.
    settings : Settings
        Persistent editor settings used for startup behavior and file dialogs.
    context_menu : WorldContextMenu
        Context menu that stores copied objects and paste target positions.
    world_view : WorldView
        Scrollable editing surface for the active world map.
    tool_window : ToolWindow
        Floating tool palette for selecting tiles and map-object edit modes.
    scroll_area : QScrollArea
        Scroll container that keeps oversized world maps navigable at any zoom.
    menu_toolbar : QToolBar | None
        Toolbar mirror of the most common menu actions once setup completes.
    file_menu : QMenu
        Menu that owns ROM, export, settings, and quit actions.
    edit_menu : EditMenu
        Undo-aware edit surface for clipboard operations and world metadata
        dialogs.
    view_menu : ViewMenu
        Zoom and rendering controls that stay synchronized with
        :class:`WorldView`.
    world_menu : QMenu
        Menu that switches between SMB3 worlds or reloads the loaded one.
    help_menu : HelpMenu
        Shared help surface narrowed to Scribe-specific about and reference
        actions.
    open_rom_action : QAction
        File-menu action that opens another ROM after the unsaved-changes gate.
    save_rom_action : QAction
        File-menu action that persists the loaded ROM in place.
    save_as_rom_action : QAction
        File-menu action that writes the loaded ROM to a newly chosen path.
    export_map_action : QAction
        File-menu action that emits the active world as the seven-file ASM
        family used by SMB3 disassembly projects.
    reload_world_action : QAction
        World-menu action that reconstructs the active world from ROM bytes and
        discards unsaved in-memory edits after confirmation.
    settings_action : QAction
        Shared action used by both the file menu and toolbar to open editor
        preferences.
    quit_rom_action : QAction
        File-menu action that closes the editor window.
    play_action : QAction
        Toolbar action that serializes the active world into a temporary ROM
        and launches the configured emulator.
    zoom_out_action : QAction
        Toolbar zoom-out control wired to the world view and window resize
        path.
    zoom_in_action : QAction
        Toolbar zoom-in control wired to the world view and window resize path.
    """

    def __init__(self, path_to_rom: str):
        """Initialize the editor shell and optionally load the startup ROM.

        The constructor stages the window in four phases: initialize shared
        editor state from the base window; open or prompt for a ROM so
        :class:`foundry.game.File.ROM` has backing data; attach Scribe menus,
        tool windows, and shortcuts around :attr:`level_ref`; and then size and
        show both windows. Toolbar actions, shortcuts, and context-menu
        callbacks depend on that sequence because they all read from the same
        loaded map and push commands into the same undo stack. That makes this
        method the place where Scribe turns the generic Foundry main-window
        shell into a world-map editor with one shared selection, one shared
        undo history, and one shared ROM-backed save pipeline.

        Parameters
        ----------
        path_to_rom : str
            Startup ROM path to load before the main and tool windows are
            shown. When empty, :meth:`on_open_rom` falls back to prompting the
            user.

        Notes
        -----
        The startup ROM is loaded before Scribe-specific widgets are created so
        menus, the world view, and the tool window all bind to a populated
        :attr:`level_ref`. The inverse order would require each surface to
        defend against a missing world and would decouple undo, export, and
        instaplay actions from the same active map.
        """
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
        self.world_view.set_zoom(3.0)

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

        self.menu_toolbar = QToolBar(_tr("toolbar.menu"), self)
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

        self.play_action = self.menu_toolbar.addAction(icon("play-circle.svg"), _tr("action.play_level"))
        self.play_action.triggered.connect(self.on_play)
        self.play_action.setWhatsThis(_tr("whats_this.play_level"))

        self.menu_toolbar.addSeparator()

        self.zoom_out_action = self.menu_toolbar.addAction(icon("zoom-out.svg"), _tr("action.zoom_out"))
        self.zoom_out_action.triggered.connect(self.world_view.zoom_out)
        self.zoom_out_action.triggered.connect(self._resize_for_level)
        self.zoom_in_action = self.menu_toolbar.addAction(icon("zoom-in.svg"), _tr("action.zoom_in"))
        self.zoom_in_action.triggered.connect(self.world_view.zoom_in)
        self.zoom_in_action.triggered.connect(self._resize_for_level)

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
        """Create file actions for ROM loading, saving, export, and settings.

        The file menu is the main entry point for switching ROMs, persisting
        edits, exporting ASM, and opening editor preferences. The same actions
        are later mirrored into the toolbar, so this setup establishes the
        canonical action objects and their enabled state first.

        Notes
        -----
        The save action tracks :attr:`undo_stack` cleanliness so the user only
        sees it enabled when the loaded world has unsaved edits.
        """
        self.file_menu = QMenu(_tr("menu.file"))
        self.file_menu.triggered.connect(self.on_file_menu)

        self.open_rom_action = self.file_menu.addAction(_tr("action.open_rom"))
        self.open_rom_action.setShortcut(Qt.Modifier.CTRL | Qt.Modifier.SHIFT | Qt.Key.Key_O)
        self.open_rom_action.setIcon(icon("folder.svg"))

        self.file_menu.addSeparator()

        self.save_rom_action = self.file_menu.addAction(_tr("action.save_rom"))
        self.save_rom_action.setShortcut(Qt.Modifier.CTRL | Qt.Key.Key_S)
        self.save_rom_action.setIcon(icon("save.svg"))

        self.save_rom_action.setEnabled(False)
        self.undo_stack.cleanChanged.connect(lambda: self.save_rom_action.setEnabled(not self.undo_stack.isClean()))

        self.save_as_rom_action = self.file_menu.addAction(_tr("action.save_rom_as"))
        self.save_as_rom_action.setShortcut(Qt.Modifier.CTRL | Qt.Modifier.SHIFT | Qt.Key.Key_S)
        self.save_as_rom_action.setIcon(icon("save.svg"))

        self.file_menu.addSeparator()

        self.export_map_action = self.file_menu.addAction(_tr("action.export_map_asm_files"))
        self.export_map_action.setIcon(icon("save.svg"))

        self.file_menu.addSeparator()

        self.settings_action = self.file_menu.addAction(_tr("action.editor_settings"))
        self.settings_action.setIcon(icon("sliders.svg"))
        self.settings_action.triggered.connect(self._on_show_settings)

        self.file_menu.addSeparator()

        self.quit_rom_action = self.file_menu.addAction(_tr("action.quit"))
        self.quit_rom_action.setIcon(icon("power.svg"))

        self.menuBar().addMenu(self.file_menu)

    def _setup_edit_menu(self):
        """Attach the edit menu and reconnect it to Scribe refresh hooks.

        The edit menu owns action dispatch for undo, redo, bulk deletion, and
        world-info editing. This setup keeps those actions attached to the
        shared world view and also listens for possible world-order changes so
        the world selector can realign with the staged metadata dialog result.
        """
        self.edit_menu = EditMenu(self)
        self.edit_menu.triggered.connect(self.world_view.update)

        self.edit_menu.world_order_maybe_changed.connect(self._on_world_order_changed)

        self.menuBar().addMenu(self.edit_menu)

    def _setup_view_menu(self):
        """Attach the view menu and resize the window after zoom changes.

        View-menu actions persist overlay settings and can change the rendered
        world size. Connecting both repaint and resize callbacks here keeps the
        scroll area, saved settings, and world renderer synchronized whenever a
        user toggles view state.
        """
        self.view_menu = ViewMenu(self, self.world_view)
        self.view_menu.triggered.connect(self.world_view.update)
        self.view_menu.triggered.connect(self._resize_for_level)

        self.menuBar().addMenu(self.view_menu)

    def _setup_level_menu(self):
        """Create world-selection actions and load world 1 on startup.

        This menu is the top-level switch for replacing the map stored in
        :attr:`level_ref`. It also keeps a reload action near the world list so
        users can throw away in-memory edits and reconstruct the same world
        directly from the loaded ROM.

        Notes
        -----
        The level menu uses one checkable action per SMB3 world plus a reload
        action. Triggering the first world action during setup ensures the rest
        of the window starts with a loaded map before user interaction.
        """
        self.world_menu = QMenu(_tr("menu.change_world"))
        self.world_menu.triggered.connect(self.on_level_menu)

        level_menu_action_group = QActionGroup(self)

        for level_index in range(WORLD_COUNT):
            action = self.world_menu.addAction(_tr("action.world").format(index=level_index + 1))
            action.setCheckable(True)

            level_menu_action_group.addAction(action)

        self.world_menu.addSeparator()

        self.reload_world_action = self.world_menu.addAction(_tr("action.reload_current_world"))
        self.reload_world_action.setIcon(icon("refresh-cw.svg"))

        # load world 1 on startup
        self.world_menu.actions()[0].trigger()

        self.menuBar().addMenu(self.world_menu)

    def _setup_help_menu(self):
        """Attach the shared help menu to the main menu bar.

        The Scribe help menu reuses Foundry's support workflow while swapping
        in Scribe-specific labels and about-dialog behavior. The main window
        only owns menu placement; the menu owns its own retranslation hook.
        """
        self.help_menu = HelpMenu(self)

        self.menuBar().addMenu(self.help_menu)

    def _on_world_order_changed(self):
        """Realign the checked world action after world-info reordering.

        The world-info dialog can change the staged world index through undo
        commands. This slot reads the active world's encoded index from the
        model and updates only the menu selection, keeping display state in
        sync without changing the loaded world again.
        """
        new_world_index = self.level_ref.level.internal_world_map.data.index

        self.world_menu.actions()[new_world_index].setChecked(True)

    def _on_show_settings(self):
        """Open the modal settings dialog for editor-wide preferences.

        The dialog writes through to the shared settings object while it is
        open. Its language signal is connected to the main-window refresh path
        so Scribe can retranslate menus, toolbars, world views, and tool
        windows without requiring a restart.
        """
        settings_dialog = SettingsDialog(self.settings, self)
        settings_dialog.language_changed.connect(self._on_language_changed)
        settings_dialog.exec()

    def _on_language_changed(self, language_code: str) -> None:
        """Apply a settings language change through the app-wide refresh path.

        Parameters
        ----------
        language_code : str
            Locale code stored by the settings dialog.

        Notes
        -----
        With an active QApplication, the localization layer installs the new
        catalog and walks open widgets for ``retranslate_ui`` hooks. The direct
        refresh is kept only for tests or unusual non-application callers.
        """
        app = QApplication.instance()
        if app is not None:
            set_application_language(app, language_code)
        else:
            self.retranslate_ui()

    def retranslate_ui(self) -> None:
        """Refresh high-traffic labels after the active translator changes.

        This is the live-language boundary for the main Scribe shell. It
        rewrites menu titles, action text, toolbar titles, tooltips, context
        menu labels, child menus, the tool window, the world view, and the
        window title from catalog keys while preserving action identity,
        checked states, shortcuts, selected world data, and undo history.
        """
        self.file_menu.setTitle(_tr("menu.file"))
        self.open_rom_action.setText(_tr("action.open_rom"))
        self.save_rom_action.setText(_tr("action.save_rom"))
        self.save_as_rom_action.setText(_tr("action.save_rom_as"))
        self.export_map_action.setText(_tr("action.export_map_asm_files"))
        self.settings_action.setText(_tr("action.editor_settings"))
        self.quit_rom_action.setText(_tr("action.quit"))
        self.edit_menu.retranslate_ui()
        self.view_menu.retranslate_ui()
        self.world_menu.setTitle(_tr("menu.change_world"))
        for index, action in enumerate(self.world_menu.actions()[:WORLD_COUNT], start=1):
            action.setText(_tr("action.world").format(index=index))
        self.reload_world_action.setText(_tr("action.reload_current_world"))
        if self.menu_toolbar is not None:
            self.menu_toolbar.setWindowTitle(_tr("toolbar.menu"))
        self.play_action.setText(_tr("action.play_level"))
        self.play_action.setWhatsThis(_tr("whats_this.play_level"))
        self.zoom_out_action.setText(_tr("action.zoom_out"))
        self.zoom_in_action.setText(_tr("action.zoom_in"))
        self.context_menu.retranslate_ui()
        self.help_menu.retranslate_ui()
        self.tool_window.retranslate_ui()
        self.world_view.retranslate_ui()
        self.setWindowTitle(_tr("window.title").format(level_name=self.level_ref.level.name))

    def _cut_objects(self):
        """Copy the active selection, then replace it with blank tiles.

        The cut workflow delegates persistence to the same blanking commands
        used by delete. Copy state stays on the context menu, while the
        removal step enters the shared undo stack through
        :meth:`remove_selected_objects`.
        """
        self._copy_objects()
        self.remove_selected_objects()

        self.world_view.update()

    def remove_selected_objects(self):
        """Blank every selected tile or object through one undo macro.

        Notes
        -----
        Deletions are expressed as :class:`scribe.gui.commands.PutTile`
        commands so removing objects participates in the same undo stack as
        other world edits.
        """
        selected_objects = [obj for obj in self.world_view.world.get_selected_tiles() if obj.selected]

        if not selected_objects:
            return

        self.undo_stack.beginMacro(_tr("undo.remove_selected_tiles"))

        for obj in selected_objects:
            self.undo_stack.push(PutTile(self.level_ref, obj.pos, WORLD_MAP_BLANK_TILE_ID))

        self.undo_stack.endMacro()

    def _copy_objects(self):
        """Store the active selection in the context-menu clipboard cache.

        The copied payload remains an in-memory world-view selection snapshot.
        It is not persisted to settings or ROM data; paste later converts that
        snapshot into undoable tile-placement commands.
        """
        selected_objects = self.world_view.get_selected_objects().copy()

        if selected_objects:
            self.context_menu.set_copied_objects(selected_objects)

        self.world_view.update()

    def _paste_objects(self, q_point: QPoint | None = None):
        """Paste copied objects relative to a chosen target position.

        This method turns the clipboard snapshot stored on the context menu into
        a batch of :class:`scribe.gui.commands.PutTile` commands. That keeps
        paste behavior aligned with manual editing and lets one undo step revert
        the whole placement.

        Parameters
        ----------
        q_point : QPoint | None, optional
            Global cursor position from the context menu. When omitted, the
            paste operation uses the world view's last tracked mouse position.

        Notes
        -----
        Pasted objects preserve their relative offsets from the original copy
        origin. Objects that would fall outside the loaded world bounds are
        skipped instead of clipped.
        """
        if not (copy_data := self.context_menu.get_copied_objects())[0]:
            return

        if q_point is not None:
            paste_target = self.world_view.to_level_point(self.world_view.mapFromGlobal(q_point))
        else:
            paste_target = self.world_view.last_mouse_position

        copied_objects, copy_origin = copy_data

        diff = paste_target - copy_origin

        self.undo_stack.beginMacro(_tr("undo.pasting_objects").format(count=len(copied_objects)))

        for obj in copied_objects:
            target_pos = Position.from_xy(*obj.get_position()) + diff

            if not self.world_view.world.point_in(*target_pos.xy):
                continue

            self.undo_stack.push(PutTile(self.level_ref, target_pos, obj.type))

        self.undo_stack.endMacro()

        self.world_view.update()

    def on_play(self, temp_dir=Path()):
        """Launch instaplay after serializing the active world into a temp ROM.

        Parameters
        ----------
        temp_dir : Path, optional
            Ignored caller-provided path placeholder kept for compatibility with
            the base-class action signature.

        Notes
        -----
        Scribe always stages instaplay files under the shared system temp
        directory in ``smb3scribe`` so repeated launches reuse the same area.
        """
        temp_dir = Path(tempfile.gettempdir()) / "smb3scribe"
        temp_dir.mkdir(parents=True, exist_ok=True)

        super(ScribeMainWindow, self).on_play(temp_dir)

    def _save_changes_to_instaplay_rom(self, path_to_temp_rom) -> bool:
        """Write the edited world map into the temporary instaplay ROM.

        This hook completes the base-window instaplay pipeline by reading the
        staged ROM copy, serializing Scribe's in-memory world edits into that
        copy, updating SMB3's starting-world byte to match the loaded map, and
        saving the modified bytes back to disk before the emulator launches it.
        In other words, it is the bridge between Scribe's undoable world-map
        editing state and the standalone ROM image that instaplay boots.

        Parameters
        ----------
        path_to_temp_rom : str | Path
            Temporary ROM path prepared by the base window.

        Returns
        -------
        bool
            ``True`` after the world data and starting-world byte have been
            written successfully.

        Notes
        -----
        The main ROM object stays untouched here. Instaplay always receives a
        temporary copy so Scribe can serialize unsaved edits for playtesting
        without mutating the user's working ROM path or resetting the undo
        stack.
        """
        temp_rom = ROM.from_file(path_to_temp_rom)
        self.world_view.world.save_to_rom(temp_rom)

        temp_rom.write(
            STARTING_WORLD_INDEX_ADDRESS,
            self.world_view.world.internal_world_map.number - 1,
        )

        temp_rom.save_to(path_to_temp_rom)

        return True

    def on_open_rom(self, path_to_rom=""):
        """Load a ROM from disk after confirming unsaved world-map changes.

        Parameters
        ----------
        path_to_rom : str, optional
            Explicit ROM path to open. When empty, the method prompts the user.

        Notes
        -----
        Cancelling the chooser exits the application only when no ROM is
        loaded yet. Once Scribe already has a ROM open, cancellation leaves the
        current editing session intact.
        """
        if not self.safe_to_change():
            return

        if not path_to_rom:
            # otherwise ask the user what new file to open
            path_to_rom, _ = QFileDialog.getOpenFileName(
                self,
                caption=_tr("dialog.open_rom.title"),
                dir=self.settings.value("editor/default_dir_path"),
                filter=ROM_FILE_FILTER,
            )

            if not path_to_rom:
                if not ROM.is_loaded():
                    sys.exit(0)
                else:
                    return

        # Proceed loading the file chosen by the user
        try:
            ROM.load_from_file(path_to_rom)
        except IOError as exp:
            QMessageBox.warning(
                self,
                type(exp).__name__,
                _tr("error.cannot_open_file").format(path=path_to_rom),
            )
            return

    def load_level(self, world_number: int):
        """Load one SMB3 world map into the shared level reference.

        Parameters
        ----------
        world_number : int
            One-based SMB3 world number to deserialize from the loaded ROM.

        Notes
        -----
        Loading a different world clears the undo stack because existing undo
        commands target the previously loaded map's addresses and dimensions.
        """
        world = SMB3WorldMap.from_world_number(ROM(), world_number)

        self.level_ref.load_level(f"World {world_number}", world.layout_address, 0x0, WORLD_MAP_OBJECT_SET)
        self.level_ref.level.dimensions_changed.connect(self._resize_for_level)

        self.setWindowTitle(_tr("window.title").format(level_name=self.level_ref.level.name))

        self.undo_stack.clear()

    def on_save_rom(self, is_save_as=False):
        """Persist the loaded ROM, optionally through Save As.

        Parameters
        ----------
        is_save_as : bool, optional
            When ``True``, prompt for a destination path instead of reusing the
            ROM's loaded path.

        Notes
        -----
        A normal save marks the undo stack clean and emits the shared
        ``data_changed`` signal so other windows can refresh from the updated
        ROM path.
        """
        if is_save_as:
            suggested_file = ROM.name

            if not suggested_file.endswith(".nes"):
                suggested_file += ".nes"

            pathname, _ = QFileDialog.getSaveFileName(
                self,
                caption=_tr("dialog.save_rom_as.title"),
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
        """Export the active world map into the seven ASM companion files.

        The export flow runs in three stages: choose a destination basename,
        derive the layout, object, coordinate, item, and structure payloads
        from the loaded :class:`foundry.game.level.WorldMap.WorldMap`, and then
        write all sibling files into one directory. Keeping those stages in one
        method makes the overwrite prompt, generated text, and emitted file set
        stay consistent. It also keeps the exported filenames tied to the same
        loaded world state, so a maintainer does not have to chase a split
        between file-dialog choices, sprite serialization, and structure-table
        generation.

        Notes
        -----
        The export mirrors the layout expected by SMB3 disassembly projects:
        separate files for layout tiles, sprite IDs, sprite coordinates, sprite
        item payloads, and the structure table that points to level metadata.
        The destination basename is resolved first because all seven output
        files must either overwrite one existing family together or create one
        new family together.
        """
        level = cast(WorldMap, self.level_ref.level)

        if True:
            # get file basename
            pathname, _ = QFileDialog.getSaveFileName(
                self,
                caption=_tr("dialog.export_map_as_asm.title"),
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
        """Build the ``S`` ASM file for one exported world map.

        This serializer groups level-pointer metadata by screen so the emitted
        labels match the split-table layout expected by SMB3 world-map ASM.

        Parameters
        ----------
        level : WorldMap
            Loaded editor world whose level pointers should be serialized.

        Returns
        -------
        str
            Assembly source containing per-screen tables for level row/object
            bytes, screen/column bytes, enemy-item offsets, and layout offsets.
        """
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

                    # Label names are not preserved in parsed world data, so export stable numeric offsets.
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
        """Build the ``L`` ASM file that stores visible world-map tiles.

        The formatter inserts line breaks at row and screen boundaries so the
        exported text remains aligned with the map's spatial layout when read by
        maintainers.

        Parameters
        ----------
        level : WorldMap
            Loaded editor world whose tile objects should be serialized.

        Returns
        -------
        str
            Assembly source grouped into SMB3 row and screen boundaries and
            terminated with the ``$FF`` end marker expected by the exporter.
        """
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
        """Choose the export basename that best matches the selected ASM path.

        This is the user-facing bridge between a single save-dialog filename and
        Scribe's seven-file export convention. It decides whether the export
        should join an existing file family or create a new basename.

        Parameters
        ----------
        path : Path
            User-selected save path from the export dialog.

        Returns
        -------
        str
            Basename used for the seven exported ASM files.

        Notes
        -----
        When the user clicks an existing member of a previously exported world
        set, this method offers to overwrite that whole set instead of creating
        a parallel basename from the clicked suffix file.
        """
        potential_base_name = self._base_name_from_world_asm(path)

        if (path.parent / f"{potential_base_name}L.asm").is_file():
            should_change_base_name = (
                QMessageBox.question(
                    self,
                    _tr("dialog.export_map_as_asm.title"),
                    _tr("dialog.export_existing_world_map.prompt").format(
                        base_name=potential_base_name,
                        selected_stem=path.stem,
                    ),
                )
                == QMessageBox.StandardButton.Yes
            )

            if should_change_base_name:
                return potential_base_name

        return path.stem

    @staticmethod
    def _base_name_from_world_asm(path: Path):
        """Collapse one exported ASM filename back to its shared world basename.

        The helper recognizes Scribe's world-export naming scheme, probes the
        neighboring sibling filenames, and yields a family root only when those
        checks confirm that the selected file belongs to a complete export set.

        Parameters
        ----------
        path : Path
            Candidate path chosen in the export dialog.

        Returns
        -------
        str
            Family basename for a complete seven-file export set, otherwise
            ``path.stem``.

        Notes
        -----
        Scribe exports seven files per world map: ``L``, ``O``, ``OH``, ``OX``,
        ``OY``, ``OI``, and ``S``. This helper only strips the suffix when the
        neighboring files exist, which avoids collapsing unrelated filenames
        such as ``TOOLS.asm`` to ``TO``.
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
        """Dispatch file-menu actions to the matching ROM workflow.

        Parameters
        ----------
        action : QAction
            Triggered menu action from the file menu.
        """
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
        """Switch or reload the active world after confirming unsaved edits.

        Parameters
        ----------
        action : QAction
            Triggered world-menu action, either a numbered world or reload.
        """
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
        """Report whether the window may discard the loaded world state.

        This guard is used before ROM loads and world switches so every workflow
        that would replace in-memory map data consults the same unsaved-changes
        policy.

        Returns
        -------
        bool
            ``True`` when there are no unsaved edits or the user confirms that
            those edits may be discarded.
        """
        return self.undo_stack.isClean() or self.confirm_changes()

    def _resize_for_level(self):
        """Resize the window to fit the loaded world view when not maximized."""
        if not self.isMaximized():
            self.resize(self.sizeHint())

    def sizeHint(self) -> QSize:
        """Return a window size that fits the loaded map view and chrome.

        The hint follows the world view's zoom-dependent size and then adds the
        surrounding Qt chrome so switching worlds or zoom levels keeps the
        editor framed without clipping the scroll area.

        Returns
        -------
        QSize
            Suggested size capped to the primary screen width and expanded to
            include scroll bars, frame widths, the menu bar, and the optional
            toolbar.
        """
        inner_width, inner_height = self.world_view.sizeHint().toTuple()

        height = inner_height + self.scroll_area.horizontalScrollBar().height() + 2 * self.scroll_area.frameWidth()
        height += self.menuBar().height()

        if self.menu_toolbar:
            height += self.menu_toolbar.height()

        width = inner_width + 2 * self.scroll_area.frameWidth()

        size_hint = QSize(min(width, QApplication.primaryScreen().size().width()), height)

        return size_hint
