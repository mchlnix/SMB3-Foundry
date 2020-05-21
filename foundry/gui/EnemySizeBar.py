from PySide2.QtCore import Qt
from PySide2.QtGui import QColor

from foundry.gui.LevelSizeBar import LevelSizeBar


class EnemySizeBar(LevelSizeBar):
    def __init__(self, parent, level):
        super(EnemySizeBar, self).__init__(parent, level)

    @property
    def value_color(self):
        return QColor.fromRgb(0xFFA140)

    @property
    def value_description(self):
        return "Enemies/Items"

    @property
    def current_value(self):
        return self.level.current_enemies_size()

    @property
    def original_value(self):
        return self.level.enemy_size_on_disk
