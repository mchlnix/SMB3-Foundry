from PySide6.QtCore import QPoint
from PySide6.QtGui import QAction, Qt

from foundry import icon
from foundry.game.level.LevelRef import LevelRef
from foundry.game.level.WorldMap import WorldMap
from foundry.gui.ContextMenu import ContextMenu


class WorldContextMenu(ContextMenu):
    def __init__(self, level_ref: LevelRef):
        super(WorldContextMenu, self).__init__(level_ref)

        self.level_ref = level_ref

        self.cut_action = self.addAction("Cut Tiles")
        self.cut_action.setShortcut(Qt.Modifier.CTRL | Qt.Key.Key_X)
        self.cut_action.setIcon(icon("scissors.svg"))

        self.copy_action = self.addAction("Copy Tiles")
        self.copy_action.setShortcut(Qt.Modifier.CTRL | Qt.Key.Key_C)
        self.copy_action.setIcon(icon("copy.svg"))

        self.paste_action = self.addAction("Paste Tiles")
        self.paste_action.setShortcut(Qt.Modifier.CTRL | Qt.Key.Key_V)
        self.paste_action.setIcon(icon("clipboard.svg"))

    @property
    def world(self) -> WorldMap:
        return self.level_ref.level

    def popup(self, pos: QPoint, at: QAction = None):
        self.copy_action.setEnabled(bool(self.world.get_selected_tiles()))
        self.cut_action.setEnabled(bool(self.world.get_selected_tiles()))

        self.paste_action.setEnabled(bool(self.copied_objects))

        return super(WorldContextMenu, self).popup(pos, at)
