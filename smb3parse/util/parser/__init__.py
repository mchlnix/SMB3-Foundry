import pathlib
import time
from collections import defaultdict
from dataclasses import dataclass
from typing import Generator

from smb3parse.constants import OFFSET_SIZE
from smb3parse.levels import HEADER_LENGTH, WORLD_COUNT
from smb3parse.levels.level_header import LevelHeader
from smb3parse.levels.world_map import WorldMap
from smb3parse.objects.object_set import MUSHROOM_OBJECT_SET, SPADE_BONUS_OBJECT_SET
from smb3parse.util.parser.cpu import NesCPU
from smb3parse.util.parser.level import ParsedLevel
from smb3parse.util.rom import Rom


@dataclass
class FoundLevel:
    level_offset_positions: list[int]
    enemy_offset_positions: list[int]

    data: ParsedLevel


def gen_levels_in_rom(rom: Rom) -> Generator[tuple[int, int], bool, tuple[defaultdict, dict[int, FoundLevel]]]:
    levels_by_address: dict[int, FoundLevel] = {}

    start = time.time()

    for world_num in range(WORLD_COUNT - 1):
        levels_in_world = 0

        world = WorldMap.from_world_number(rom, world_num + 1)

        level_tuples = [
            (lp.level_address, lp.level_offset_address, lp.enemy_address, lp.enemy_offset_address, lp.object_set)
            for lp in world.level_pointers
        ]

        # add airship
        level_tuples.append(
            (
                world.data.airship_level_address,
                world.data.airship_level_offset_address,
                world.data.airship_enemy_offset,
                world.data.airship_enemy_offset_address,
                world.data.airship_level_object_set,
            )
        )

        # add generic exit
        level_tuples.append(
            (
                world.data.generic_exit_level_address,
                world.data.generic_exit_level_offset_address,
                world.data.generic_exit_enemy_offset,
                world.data.generic_exit_enemy_offset_address,
                world.data.generic_exit_object_set,
            )
        )

        # add big ? level
        level_tuples.append(
            (
                world.data.big_q_block_level_address,
                world.data.big_q_block_level_offset_address,
                world.data.big_q_block_enemy_offset,
                world.data.big_q_block_enemy_offset_address,
                world.data.big_q_block_object_set,
            )
        )

        # add coin ship level
        level_tuples.append(
            (
                world.data.coin_ship_level_address,
                world.data.coin_ship_level_offset_address,
                world.data.coin_ship_enemy_offset,
                world.data.coin_ship_enemy_offset_address,
                world.data.coin_ship_level_object_set,
            )
        )

        # add special/white toad house level
        level_tuples.append(
            (
                world.data.toad_warp_level_address,
                world.data.toad_warp_level_offset_address,
                0x0,  # enemy item data is used directly, not as an offset
                world.data.toad_warp_item_address,
                MUSHROOM_OBJECT_SET,
            ),
        )

        should_stop = False
        for (
            level_address,
            level_address_position,
            enemy_address,
            enemy_address_position,
            object_set_number,
        ) in level_tuples:
            if should_stop:
                return defaultdict(list), levels_by_address

            if level_address in levels_by_address:
                found_level = levels_by_address[level_address]

                assert level_address_position not in found_level.level_offset_positions
                found_level.level_offset_positions.append(level_address_position)

                assert enemy_address_position not in found_level.enemy_offset_positions
                found_level.enemy_offset_positions.append(enemy_address_position)

                continue

            if object_set_number == SPADE_BONUS_OBJECT_SET:
                continue

            print(f"W{world_num + 1}", hex(level_address), hex(enemy_address), object_set_number)
            # traverse Jump Destinations by following the offsets in the header
            while True:
                levels_in_world += 1

                should_stop = yield world.number, levels_in_world

                if should_stop:
                    break

                parsed_level = NesCPU(rom).load_from_address(object_set_number, level_address, enemy_address)
                found_level = FoundLevel([level_address_position], [enemy_address_position], parsed_level)

                levels_by_address[level_address] = found_level

                if not parsed_level.has_jump():
                    break

                header_of_old_level = LevelHeader(rom.read(level_address, HEADER_LENGTH), object_set_number)

                object_set_number = header_of_old_level.jump_object_set_number

                level_address = header_of_old_level.jump_level_address
                level_address_position = level_address

                enemy_address = header_of_old_level.jump_enemy_address
                enemy_address_position = level_address + OFFSET_SIZE

                if 0 in [header_of_old_level.jump_level_offset, object_set_number]:
                    break

                if level_address in levels_by_address:
                    break

                print("    ", hex(level_address), object_set_number)

    print(time.time() - start)

    level_count = 0

    levels_per_object_set = defaultdict(list)

    for level_address in sorted(levels_by_address.keys()):
        found_level = levels_by_address[level_address]
        levels_per_object_set[found_level.data.object_set_num].append(level_address)

    for object_set, levels_addresses in sorted(levels_per_object_set.items()):
        level_count += len(levels_addresses)
        print(
            object_set,
            ": ",
            len(levels_addresses),
            ", ".join(
                f"{hex(level_address).upper().replace('X', 'x')}/"
                f"{len(levels_by_address[level_address].level_offset_positions)}"
                for level_address in sorted(levels_addresses)
            ),
        )

    print("---------------------", level_count, "------------------------")

    level_data = pathlib.Path("data/levels.dat")

    missing = 0
    levels: dict[int, set[int]] = defaultdict(set)

    for line in level_data.open("r").readlines():
        if not line:
            continue

        world_no, *_, level_address, _, object_set_no, _ = line.split(",")

        level_address = int(level_address, 16) - 9
        object_set_num = int(object_set_no, 16)

        if int(world_no) in [0, 9]:
            continue

        levels[object_set_num].add(level_address)

        if level_address not in levels_per_object_set[object_set_num]:
            missing += 1
            print(world_no, object_set_num, hex(level_address))

    print(missing, "levels")

    for object_set_num in range(1, 15):
        print(
            object_set_num,
            list(map(hex, set(levels_per_object_set[object_set_num]).difference(levels[object_set_num]))),
        )

    return levels_per_object_set, levels_by_address
