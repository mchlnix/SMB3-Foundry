"""Host ROM-wide viewer and maintenance actions for the editor shell.

This module owns the ROM menu in Foundry's main window. The menu sits in the
editor workflow between the loaded ROM and a set of auxiliary viewers or
dialogs: it surfaces ROM-wide actions in the menu bar, dispatches the chosen
action into either a reusable viewer window or a one-shot dialog, and emits a
refresh signal when a ROM-wide mutation invalidates the active editor UI. That
keeps ROM inspection and ROM maintenance on one route separate from the
per-object editing workflow in the level canvas.

See Also
--------
foundry.gui.FoundryMainWindow
    Owns the menu bar and reacts to the refresh signal emitted here.
foundry.gui.windows.LevelViewer
    ROM-scanning viewer opened from this menu.
foundry.gui.rom_settings.rom_settings_dialog
    Dialog that edits persistent ROM-level settings.
"""

from collections import defaultdict

from PySide6.QtCore import Signal, SignalInstance
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QDialog, QMenu, QMessageBox

from foundry import icon
from foundry.game.File import ROM
from foundry.game.gfx.objects import LevelObject
from foundry.game.level.LevelRef import LevelRef
from foundry.gui.dialogs.GamePropertiesDialog import GamePropertiesDialog
from foundry.gui.dialogs.LevelParseProgressDialog import LevelParseProgressDialog
from foundry.gui.dialogs.PaletteViewer import PaletteViewer
from foundry.gui.rom_settings.rom_settings_dialog import RomSettingsDialog
from foundry.gui.windows.BlockViewer import BlockViewer
from foundry.gui.windows.LevelViewer import LevelViewer
from foundry.gui.windows.ObjectViewer import ObjectViewer


class RomMenu(QMenu):
    """Expose ROM inspection and ROM-wide maintenance actions.

    The ROM menu groups tools that look beyond the selection in the editing
    canvas. It opens viewers for decoded blocks, objects, palettes, and scanned
    levels in memory, and it hosts ROM-wide maintenance actions such as clearing
    editor metadata or editing persistent ROM settings.

    Parameters
    ----------
    level_ref : LevelRef
        Shared reference to the active level and its selection state.
    title : str, optional
        Menu title shown in the main window.

    Attributes
    ----------
    _block_viewer : BlockViewer | None
        Lazily created block viewer window.
    _clear_editor_data_action : QAction
        Action that clears Foundry-managed metadata from the ROM.
    _level_ref : LevelRef
        Active level reference used to seed viewers with the open level's
        context.
    _level_viewer : LevelViewer | None
        Lazily created level-in-memory viewer window.
    _object_viewer : ObjectViewer | None
        Lazily created object viewer window.
    _view_blocks_action : QAction
        Action that opens the block viewer.
    _view_levels_in_memory_action : QAction
        Action that opens the scanned level viewer.
    _view_objects_action : QAction
        Action that opens the object viewer.
    _view_palettes_action : QAction
        Action that opens the palette viewer.
    game_properties_action : QAction
        Action that edits ROM-level game properties.
    needs_gui_refresh : SignalInstance
        Signal emitted after actions that invalidate the open editor state.
    rom_settings_action : QAction
        Action that opens the ROM settings dialog.
    """

    needs_gui_refresh: SignalInstance = Signal()

    def __init__(self, level_ref: LevelRef, title="&Rom"):
        """Create the ROM menu for the active editor session.

        Construction stores the active ``LevelRef``, initializes the lazily
        created viewer handles to ``None``, connects the central trigger
        dispatcher, and then registers the actions in the same groups the user
        sees at runtime: viewers, palette inspection, ROM scanning, ROM-wide
        property editing, and ROM-maintenance actions. The menu therefore sets
        up two later workflows at once: action dispatch into one-off dialogs
        such as ``GamePropertiesDialog`` and lazy creation or reuse of the
        longer-lived viewer windows.

        Parameters
        ----------
        level_ref : LevelRef
            Shared reference to the active level and its selection state.
        title : str, optional
            Menu title shown in the main window.
        """
        super(RomMenu, self).__init__(title)

        self._level_ref = level_ref
        self._level_viewer: LevelViewer | None = None
        self._block_viewer: BlockViewer | None = None
        self._object_viewer: ObjectViewer | None = None

        self.triggered.connect(self._on_trigger)

        self._view_blocks_action = self.addAction("View Blocks")
        self._view_blocks_action.setIcon(icon("grid.svg"))

        self._view_objects_action = self.addAction("View Objects")
        self._view_objects_action.setIcon(icon("star.svg"))

        self.addSeparator()

        self._view_palettes_action = self.addAction("View Object Palettes")
        self._view_palettes_action.setIcon(icon("figma.svg"))

        self.addSeparator()

        self._view_levels_in_memory_action = self.addAction("View Levels in Memory")
        self._view_levels_in_memory_action.setIcon(icon("server.svg"))

        self.addSeparator()

        self.game_properties_action = self.addAction("Game Properties")
        self.game_properties_action.setIcon(icon("bar-chart-2.svg"))

        self.addSeparator()

        self.rom_settings_action = self.addAction("ROM Settings")
        self.rom_settings_action.setIcon(icon("settings.svg"))

        self._clear_editor_data_action = self.addAction("Clear Editor Data in ROM")
        self._clear_editor_data_action.setIcon(icon("loader.svg"))

    def _on_trigger(self, action: QAction):
        """Dispatch ROM-menu actions to the matching tool or dialog.

        Parameters
        ----------
        action : QAction
            Triggered action from this menu.
        """
        match action:
            case self._view_levels_in_memory_action:
                self._show_level_viewer()

            case self._view_blocks_action:
                self._show_block_viewer()

            case self._view_objects_action:
                self._show_object_viewer()

            case self._view_palettes_action:
                PaletteViewer(self.parent(), self._level_ref).exec()

            case self._clear_editor_data_action:
                ROM.additional_data.clear()
                self.needs_gui_refresh.emit()

            case self.rom_settings_action:
                dialog = RomSettingsDialog(self.parent(), self._level_ref)
                dialog.needs_gui_update.connect(self.needs_gui_refresh.emit)

                dialog.exec()

            case self.game_properties_action:
                try:
                    prop_dialog = GamePropertiesDialog(self.parent(), ROM())
                except ValueError as ve:
                    QMessageBox.critical(self.parent(), "Error opening Game Properties", str(ve))
                    return

                result = prop_dialog.exec()

                if result == QDialog.Accepted:
                    ROM.save_to_file(ROM.path)

    def _show_level_viewer(self):
        """Open the level-in-memory viewer, parsing levels on demand.

        When managed level positions are already available in `ROM.additional_data`,
        the viewer reuses them. Otherwise it runs the progress dialog that scans
        the ROM and then caches the discovered levels for inspection.
        """
        levels_per_object_set: dict[int, set[int]] = defaultdict(set)
        levels_by_address = {}

        if not self._level_viewer:
            if ROM.additional_data.managed_level_positions:
                for found_level in ROM.additional_data.found_levels:  # noqa
                    levels_per_object_set[found_level.object_set_number].add(found_level.level_offset)

                levels_by_address = {
                    found_level.level_offset: found_level for found_level in ROM.additional_data.found_levels
                }

            else:
                pd = LevelParseProgressDialog()

                if not pd.wasCanceled():
                    levels_per_object_set = pd.levels_per_object_set
                    levels_by_address = pd.levels_by_address

            if levels_per_object_set:
                self._level_viewer = LevelViewer(self.parent(), levels_per_object_set, levels_by_address)

        if self._level_viewer:
            self._level_viewer.show()
            self._level_viewer.showNormal()

    def _show_block_viewer(self):
        """Open the block viewer seeded with the active level's render state."""
        if self._block_viewer is None:
            self._block_viewer = BlockViewer(parent=self.parent())

        if self._level_ref.level is not None:
            self._block_viewer.object_set = self._level_ref.object_set.number
            self._block_viewer.palette_group = self._level_ref.object_palette_index
            self._block_viewer.graphics_set_number = self._level_ref.graphic_set

        self._block_viewer.show()
        self._block_viewer.showNormal()

    def _show_object_viewer(self):
        """Open the object viewer for the loaded level's object-set context.

        The viewer follows the loaded level's object set and graphics set. When
        a level object is selected, the viewer also highlights that object's
        domain, index, and length so the browser stays aligned with the active
        edit target instead of opening as a disconnected catalog window.
        """
        if self._object_viewer is None:
            self._object_viewer = ObjectViewer(parent=self.parent())

        if self._level_ref.level is not None:
            object_set = self._level_ref.object_set.number
            graphics_set = self._level_ref.graphic_set

            self._object_viewer.set_object_and_graphic_set(object_set, graphics_set)

            if self._level_ref.selected_objects:
                obj = self._level_ref.selected_objects[0]

                if isinstance(obj, LevelObject):
                    self._object_viewer.set_object(obj.domain, obj.obj_index, obj.length)

        self._object_viewer.show()
        self._object_viewer.showNormal()

    def close_everything(self):
        """Close any auxiliary viewer windows owned by this menu."""
        if self._level_viewer:
            self._level_viewer.close()

        if self._block_viewer:
            self._block_viewer.close()

        if self._object_viewer:
            self._object_viewer.close()
