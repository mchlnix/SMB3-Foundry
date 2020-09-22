
from PySide2.QtWidgets import QWidget, QMessageBox

from smb3parse.levels.world_map import WorldMap
from smb3parse.util.rom import Rom
from smb3parse.constants import TILE_LEVEL_1

from foundry.game.level.LevelRef import LevelRef

from foundry.core.Observables.ObservableDecorator import ObservableDecorator
from foundry.core.Action.Action import Action


class ActionSaveToFirstLevel(Action):
    """Saves the rom to the first level"""
    def __init__(self, name: str, parent: QWidget, level_ref: LevelRef):
        self.name = name
        self.observer = ObservableDecorator(self._save_to_first_level)
        self.parent = parent
        self.level_ref = level_ref

    def _save_to_first_level(self, path_to_rom: str):
        """Does the action of saving to the first level"""
        result = _put_current_level_to_level_1_1(self.parent, self.level_ref, path_to_rom)
        return result


def _put_current_level_to_level_1_1(parent: QWidget, level_ref: LevelRef, path_to_rom: str) -> bool:
    with open(path_to_rom, "rb") as smb3_rom:
        data = smb3_rom.read()

    rom = Rom(bytearray(data))

    # load world-1 data
    world_1 = WorldMap.from_world_number(rom, 1)

    # find position of "level 1" tile in world map
    for position in world_1.gen_positions():
        if position.tile() == TILE_LEVEL_1:
            break
    else:
        QMessageBox.critical(
            parent, "Couldn't place level", "Could not find a level 1 tile in World 1 to put your level at."
        )
        return False

    if not level_ref.level.attached_to_rom:
        QMessageBox.critical(
            parent,
            "Couldn't place level",
            "The Level is not part of the rom yet (M3L?). Try saving it into the ROM first.",
        )
        return False

    # write level and enemy data of current level
    (layout_address, layout_bytes), (enemy_address, enemy_bytes) = level_ref.level.to_bytes()
    rom.write(layout_address, layout_bytes)
    rom.write(enemy_address, enemy_bytes)

    # replace level information with that of current level
    object_set_number = level_ref.object_set_number

    world_1.replace_level_at_position((layout_address, enemy_address - 1, object_set_number), position)

    # save rom
    rom.save_to(path_to_rom)

    return True


