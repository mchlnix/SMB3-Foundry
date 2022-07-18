from typing import Optional

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu

from foundry.game.gfx.objects.LevelObject import LevelObject
from foundry.game.level.LevelRef import LevelRef
from foundry.gui.BlockViewer import BlockViewer
from foundry.gui.ObjectViewer import ObjectViewer
from foundry.gui.PaletteViewer import PaletteViewer


class ObjectMenu(QMenu):
    def __init__(self, level_ref: LevelRef, title="&Objects"):
        super(ObjectMenu, self).__init__(title)

        self._level_ref = level_ref
        self._block_viewer: Optional[BlockViewer] = None
        self._object_viewer: Optional[ObjectViewer] = None

        self.triggered.connect(self._on_trigger)

        self._view_blocks_action = self.addAction("View &Blocks")
        self._view_objects_action = self.addAction("View &Objects")

        self.addSeparator()

        self._view_palettes_action = self.addAction("View Object &Palettes")

    def _on_trigger(self, action: QAction):
        if action is self._view_blocks_action:
            if self._block_viewer is None:
                self._block_viewer = BlockViewer(parent=self)

            if self._level_ref.level is not None:
                self._block_viewer.object_set = self._level_ref.object_set.number
                self._block_viewer.palette_group = self._level_ref.object_palette_index

            self._block_viewer.show()

        elif action is self._view_objects_action:
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
        elif action is self._view_palettes_action:
            PaletteViewer(self, self._level_ref).exec()
