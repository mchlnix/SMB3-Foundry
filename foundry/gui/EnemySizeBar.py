from PySide6.QtGui import QColor

from foundry.game.File import ROM
from foundry.gui.LevelSizeBar import LevelSizeBar


class EnemySizeBar(LevelSizeBar):
    def __init__(self, parent, level):
        super(EnemySizeBar, self).__init__(parent, level)

        self.setWhatsThis(
            "<b>Enemy Size Bar</b><br/>"
            "The enemies and items inside a level, like goombas or certain platforms, are stored as bytes in the "
            "ROM. This information is stored separately from the level objects, because multiple levels can share "
            "enemy data. Since enemy data is stored one after another, saving a level with more enemies, than "
            "it originally had, would overwrite another set of enemy data and probably cause the game to crash, if you "
            "would enter a level with broken enemy data while playing.<br/>"
            "This bar shows, how much of the available space for enemies and items is currently taken up. It will turn "
            "red, when too many enemies have been placed."
        )

    @property
    def value_color(self):
        return QColor.fromRgb(0xFFA140)

    @property
    def value_description(self):
        return "Enemies/Items"

    @property
    def current_value(self):
        return self.level_ref.current_enemies_size()

    @property
    def original_value(self):
        enemy_size = self.level_ref.enemy_size_on_disk

        if not self.level_ref.level.attached_to_rom and enemy_size == 0:
            enemy_size = float("INF")

        elif ROM().additional_data:
            free_space_in_bank = ROM().additional_data.free_space_for_enemies()
            enemy_size += free_space_in_bank

        return enemy_size
