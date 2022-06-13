from foundry.game.level.LevelRef import LevelRef
from foundry.gui.ContextMenu import ContextMenu
from smb3parse.levels.WorldMapPosition import WorldMapPosition


class WorldContextMenu(ContextMenu):
    def __init__(self, level_ref: LevelRef):
        super(WorldContextMenu, self).__init__()

        self.level_ref = level_ref

        self.copy_action = self.addAction("Copy")
        self.paste_action = self.addAction("Paste")
        self.cut_action = self.addAction("Cut")

        self.addSeparator()

        self.add_sprite_action = self.addAction("Add Sprite")
        self.remove_sprite_action = self.addAction("Remove Sprite")

    def setup_menu(self, world_map_position: WorldMapPosition) -> "WorldContextMenu":
        self.add_sprite_action.setEnabled(not world_map_position.has_sprite())
        self.remove_sprite_action.setEnabled(world_map_position.has_sprite())

        return self
