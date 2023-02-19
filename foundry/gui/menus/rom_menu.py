from collections import defaultdict
from typing import Optional

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu

from foundry import icon
from foundry.game.File import ROM
from foundry.game.gfx.objects import LevelObject
from foundry.game.level.LevelRef import LevelRef
from foundry.gui.BlockViewer import BlockViewer
from foundry.gui.LevelParseProgressDialog import LevelParseProgressDialog
from foundry.gui.LevelViewer import LevelViewer
from foundry.gui.ObjectViewer import ObjectViewer
from foundry.gui.PaletteViewer import PaletteViewer
from foundry.gui.rom_settings.rom_settings_dialog import RomSettingsDialog


class RomMenu(QMenu):
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

        self._clear_editor_data_action = self.addAction("Clear Editor Data in ROM")
        self._clear_editor_data_action.setIcon(icon("loader.svg"))

        self._rom_settings_action = self.addAction("ROM Settings")
        self._rom_settings_action.setIcon(icon("settings.svg"))

    def _on_trigger(self, action: QAction):
        match action:
            case self._view_levels_in_memory_action:
                if ROM.additional_data.managed_level_positions:
                    levels_per_object_set: dict[int, set[int]] = defaultdict(set)

                    for found_level in ROM.additional_data.found_level_information:
                        levels_per_object_set[found_level.object_set_number].add(found_level.level_offset)

                    levels_by_address = {
                        found_level.level_offset: found_level
                        for found_level in ROM.additional_data.found_level_information
                    }

                else:
                    pd = LevelParseProgressDialog()

                    if pd.wasCanceled():
                        return

                    levels_per_object_set = pd.levels_per_object_set
                    levels_by_address = pd.levels_by_address

                self._level_viewer = LevelViewer(self, levels_per_object_set, levels_by_address)
                self._level_viewer.show()

            case self._view_blocks_action:
                if self._block_viewer is None:
                    self._block_viewer = BlockViewer(parent=self)

                if self._level_ref.level is not None:
                    self._block_viewer.object_set = self._level_ref.object_set.number
                    self._block_viewer.palette_group = self._level_ref.object_palette_index

                self._block_viewer.show()

            case self._view_objects_action:
                if self._object_viewer is None:
                    self._object_viewer = ObjectViewer(parent=self)

                if self._level_ref.level is not None:
                    object_set = self._level_ref.object_set.number
                    graphics_set = self._level_ref.graphic_set

                    self._object_viewer.set_object_and_graphic_set(object_set, graphics_set)

                    if self._level_ref.selected_objects:
                        obj = self._level_ref.selected_objects[0]

                        if isinstance(obj, LevelObject):
                            self._object_viewer.set_object(obj.domain, obj.obj_index, obj.length)

                self._object_viewer.show()

            case self._view_palettes_action:
                PaletteViewer(self, self._level_ref).exec()

            case self._clear_editor_data_action:
                ROM.additional_data.clear()

            case self._rom_settings_action:
                RomSettingsDialog(self).exec()
