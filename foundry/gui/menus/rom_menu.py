from collections import defaultdict
from typing import Optional

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
    needs_gui_refresh: SignalInstance = Signal()

    def __init__(self, level_ref: LevelRef, title="&Rom"):
        super(RomMenu, self).__init__(title)

        self._level_ref = level_ref
        self._level_viewer: Optional[LevelViewer] = None
        self._block_viewer: Optional[BlockViewer] = None
        self._object_viewer: Optional[ObjectViewer] = None

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
        levels_per_object_set: dict[int, set[int]] = defaultdict(set)
        levels_by_address = {}

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
            self._level_viewer.show()

    def _show_block_viewer(self):
        if self._block_viewer is None:
            self._block_viewer = BlockViewer(parent=self.parent())

        if self._level_ref.level is not None:
            self._block_viewer.object_set = self._level_ref.object_set.number
            self._block_viewer.palette_group = self._level_ref.object_palette_index

        self._block_viewer.show()

    def _show_object_viewer(self):
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
