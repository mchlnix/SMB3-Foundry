import pathlib
import time
from collections import defaultdict

from PySide6.QtWidgets import QApplication, QProgressDialog

from foundry.game.File import ROM
from foundry.game.ObjectSet import OBJECT_SET_NAMES
from smb3parse.levels import HEADER_LENGTH, WORLD_COUNT
from smb3parse.levels.level_header import LevelHeader
from smb3parse.levels.world_map import WorldMap
from smb3parse.objects.object_set import MUSHROOM_OBJECT_SET, SPADE_BONUS_OBJECT_SET
from smb3parse.util.parser.cpu import NesCPU
from smb3parse.util.parser.level import ParsedLevel


class LevelParseProgressDialog(QProgressDialog):
    def __init__(self):
        super(LevelParseProgressDialog, self).__init__(
            "Parsing World Maps to find Levels.", "Cancel", 0, WORLD_COUNT - 1
        )

        self.levels_per_object_set: dict[int, set[int]] = defaultdict(set)
        self.levels_by_address: dict[int, ParsedLevel] = {}

        self.setWindowTitle("Parsing World Maps to find Levels")
        self.forceShow()

        QApplication.processEvents()

        self._get_all_levels()

    def _get_all_levels(self):
        rom = ROM()

        start = time.time()

        for world_num in range(WORLD_COUNT - 1):
            levels_in_world = 0

            world = WorldMap.from_world_number(rom, world_num + 1)

            level_tuples = [(lp.level_address, lp.enemy_address, lp.object_set) for lp in world.level_pointers]

            # add airship
            level_tuples.append(
                (world.data.airship_level_address, world.data.airship_enemy_offset, world.data.airship_level_object_set)
            )

            # add generic exit
            level_tuples.append(
                (
                    world.data.generic_exit_level_address,
                    world.data.generic_exit_level_offset,
                    world.data.generic_exit_object_set,
                )
            )

            # add big ? level
            level_tuples.append(
                (
                    world.data.big_q_block_level_address,
                    world.data.big_q_block_enemy_offset,
                    world.data.big_q_block_object_set,
                )
            )

            # add coin ship level
            level_tuples.append(
                (
                    world.data.coin_ship_level_address,
                    world.data.coin_ship_enemy_offset,
                    world.data.coin_ship_level_object_set,
                )
            )

            # add special/white toad house level
            level_tuples.append(
                (
                    world.data.toad_warp_level_address,
                    0x0,  # enemy item data is used directly, not as an offset
                    MUSHROOM_OBJECT_SET,
                ),
            )

            for level_address, enemy_address, object_set_number in level_tuples:
                if self.wasCanceled():
                    break

                self.setValue(world_num)

                if level_address in self.levels_per_object_set[object_set_number]:
                    continue

                if object_set_number in [SPADE_BONUS_OBJECT_SET]:
                    continue

                print(f"W{world_num + 1}", hex(level_address), hex(enemy_address), OBJECT_SET_NAMES[object_set_number])
                # traverse Jump Destinations by following the offsets in the header
                while not self.wasCanceled():
                    levels_in_world += 1
                    self.setLabelText(f"Parsing World {world.number}. Found Levels: {levels_in_world}")
                    QApplication.processEvents()

                    parsed_level = NesCPU(rom).load_from_address(object_set_number, level_address, enemy_address)
                    self.levels_per_object_set[object_set_number].add(level_address)
                    self.levels_by_address[level_address] = parsed_level

                    if not parsed_level.has_jump():
                        break

                    header_of_old_level = LevelHeader(rom.read(level_address, HEADER_LENGTH), object_set_number)

                    object_set_number = header_of_old_level.jump_object_set_number

                    level_address = header_of_old_level.jump_level_address

                    if 0 in [header_of_old_level.jump_level_offset, object_set_number]:
                        break

                    if level_address in self.levels_per_object_set[object_set_number]:
                        break

                    print("    ", hex(level_address), OBJECT_SET_NAMES[object_set_number])

        if not self.wasCanceled():
            self.setValue(WORLD_COUNT - 1)

        print(time.time() - start)

        level_count = 0

        for object_set, levels in sorted(self.levels_per_object_set.items()):
            level_count += len(levels)
            print(
                object_set,
                ": ",
                len(levels),
                ", ".join(hex(level).upper().replace("X", "x") for level in sorted(levels)),
            )

        print("---------------------", level_count, "------------------------")

        level_data = pathlib.Path("data/levels.dat")

        missing = 0
        levels: dict[int, set[int]] = defaultdict(set)

        for line in level_data.open("r").readlines():
            if not line:
                continue

            world, *_, level_address, _, object_set, _ = line.split(",")

            level_address = int(level_address, 16) - 9
            object_set = int(object_set, 16)

            if int(world) in [0, 9]:
                continue

            levels[object_set].add(level_address)

            if level_address not in self.levels_per_object_set[object_set]:
                missing += 1
                print(world, OBJECT_SET_NAMES[object_set], hex(level_address))

        print(missing, "levels")

        for object_set in range(1, 15):
            print(
                OBJECT_SET_NAMES[object_set],
                list(map(hex, self.levels_per_object_set[object_set].difference(levels[object_set]))),
            )
