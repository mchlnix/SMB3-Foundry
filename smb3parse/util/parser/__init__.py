import pathlib
import time
from collections import defaultdict
from dataclasses import dataclass
from typing import Generator

from smb3parse.constants import OFFSET_SIZE
from smb3parse.data_points import LevelPointerData
from smb3parse.levels import HEADER_LENGTH, WORLD_COUNT
from smb3parse.levels.level_header import LevelHeader
from smb3parse.levels.world_map import WorldMap
from smb3parse.objects.object_set import MUSHROOM_OBJECT_SET, SPADE_BONUS_OBJECT_SET
from smb3parse.util import hex_int
from smb3parse.util.parser.cpu import NesCPU
from smb3parse.util.rom import Rom


@dataclass
class FoundLevel:
    level_offset_positions: list[int]
    enemy_offset_positions: list[int]

    world_number: int

    level_offset: int
    enemy_offset: int

    object_set_number: int
    object_data_length: int
    """Length of all Level Objects, including the Level Header, but without the delimiter at the end."""

    enemy_data_length: int
    """Length of all Enemy Objects, without the delimiter at the beginning and end."""

    found_in_world: bool
    found_as_jump: bool
    is_generic: bool

    def to_dict(self) -> dict[str, list[int] | int | bool]:
        ret_dict = vars(self)

        return ret_dict

    @staticmethod
    def from_dict(data: dict) -> "FoundLevel":
        return FoundLevel(
            data["level_offset_positions"],
            data["enemy_offset_positions"],
            data["world_number"],
            data["level_offset"],
            data["enemy_offset"],
            data["object_set_number"],
            data["object_data_length"],
            data["enemy_data_length"],
            data["found_in_world"],
            data["found_as_jump"],
            data["is_generic"],
        )


@dataclass
class FoundLevelRecord:
    level_address: int
    level_address_offset: int

    enemy_address: int
    enemy_address_offset: int

    object_set: int

    found_in_world: bool = False
    found_as_jump: bool = False
    is_generic: bool = False

    @staticmethod
    def from_level_pointer(
        level_pointer: LevelPointerData,
        from_world: bool,
        from_jump: bool,
        generic: bool,
    ) -> "FoundLevelRecord":
        return FoundLevelRecord(
            level_pointer.level_address,
            level_pointer.level_offset_address,
            level_pointer.enemy_address,
            level_pointer.enemy_offset_address,
            level_pointer.object_set,
            from_world,
            from_jump,
            generic,
        )


def gen_levels_in_rom(
    rom: Rom,
) -> Generator[tuple[int, int], bool, tuple[defaultdict, dict[int, FoundLevel]]]:
    levels_by_address: dict[int, FoundLevel] = {}

    start = time.time()

    for world_num in range(WORLD_COUNT - 1):
        levels_in_world = 0

        world = WorldMap.from_world_number(rom, world_num + 1)

        found_level_records: list[FoundLevelRecord] = [
            (FoundLevelRecord.from_level_pointer(lp, True, False, False)) for lp in world.level_pointers
        ]

        # add airship
        found_level_records.append(
            FoundLevelRecord(
                world.data.airship_level_address,
                world.data.airship_level_offset_address,
                world.data.airship_enemy_address,
                world.data.airship_enemy_offset_address,
                world.data.airship_level_object_set,
                False,
                False,
                True,
            )
        )

        # add generic exit
        found_level_records.append(
            FoundLevelRecord(
                world.data.generic_exit_level_address,
                world.data.generic_exit_level_offset_address,
                world.data.generic_exit_enemy_address,
                world.data.generic_exit_enemy_offset_address,
                world.data.generic_exit_object_set,
                False,
                False,
                True,
            )
        )

        # add big ? level
        found_level_records.append(
            FoundLevelRecord(
                world.data.big_q_block_level_address,
                world.data.big_q_block_level_offset_address,
                world.data.big_q_block_enemy_address,
                world.data.big_q_block_enemy_offset_address,
                world.data.big_q_block_object_set,
                False,
                False,
                True,
            )
        )

        # add coin ship level
        found_level_records.append(
            FoundLevelRecord(
                world.data.coin_ship_level_address,
                world.data.coin_ship_level_offset_address,
                world.data.coin_ship_enemy_address,
                world.data.coin_ship_enemy_offset_address,
                world.data.coin_ship_level_object_set,
                False,
                False,
                True,
            )
        )

        # add special/white toad house level
        found_level_records.append(
            FoundLevelRecord(
                world.data.toad_warp_level_address,
                world.data.toad_warp_level_offset_address,
                0x0,  # enemy item data is used directly, not as an offset
                world.data.toad_warp_item_address,
                MUSHROOM_OBJECT_SET,
                False,
                False,
                True,
            ),
        )

        should_stop = False
        for record in found_level_records:
            if should_stop:
                return defaultdict(list), levels_by_address

            if record.level_address in levels_by_address:
                found_level = levels_by_address[record.level_address]

                assert record.level_address_offset not in found_level.level_offset_positions
                found_level.level_offset_positions.append(record.level_address_offset)

                assert record.enemy_address_offset not in found_level.enemy_offset_positions
                found_level.enemy_offset_positions.append(record.enemy_address_offset)

                found_level.found_in_world |= record.found_in_world
                found_level.found_as_jump |= record.found_as_jump
                found_level.is_generic |= record.is_generic

                continue

            if record.object_set == SPADE_BONUS_OBJECT_SET:
                continue

            print(
                f"W{world_num + 1}",
                hex(record.level_address),
                hex(record.enemy_address),
                record.object_set,
            )
            # traverse Jump Destinations by following the offsets in the header
            while True:
                levels_in_world += 1

                should_stop = yield world.number, levels_in_world

                if should_stop:
                    break

                parsed_level = NesCPU(rom).load_from_address(
                    record.object_set, record.level_address, record.enemy_address
                )

                found_level = FoundLevel(
                    [record.level_address_offset],
                    [record.enemy_address_offset],
                    world_num + 1,
                    record.level_address,
                    record.enemy_address,
                    record.object_set,
                    parsed_level.object_data_length,
                    parsed_level.enemy_data_length,
                    record.found_in_world,
                    record.found_as_jump,
                    record.is_generic,
                )

                levels_by_address[record.level_address] = found_level

                if not parsed_level.has_jump():
                    break

                header_of_old_level = LevelHeader(
                    rom,
                    rom.read(record.level_address, HEADER_LENGTH),
                    record.object_set,
                )

                level_address_position = record.level_address
                level_address = header_of_old_level.jump_level_address

                enemy_address_position = record.level_address + OFFSET_SIZE
                enemy_address = header_of_old_level.jump_enemy_address

                object_set_number = header_of_old_level.jump_object_set_number

                new_record = FoundLevelRecord(
                    level_address,
                    level_address_position,
                    enemy_address,
                    enemy_address_position,
                    object_set_number,
                )

                if 0 in [header_of_old_level.jump_level_offset, object_set_number]:
                    break

                if level_address in levels_by_address:
                    found_level = levels_by_address[level_address]
                    assert level_address_position not in found_level.level_offset_positions
                    found_level.level_offset_positions.append(level_address_position)
                    found_level.enemy_offset_positions.append(enemy_address_position)
                    found_level.found_as_jump = True
                    break

                new_record.found_in_world = False
                new_record.found_as_jump = True

                record = new_record

                print("    ", hex(level_address), object_set_number)

    print(time.time() - start)

    level_count = 0

    levels_per_object_set = defaultdict(list)

    for level_address in sorted(levels_by_address.keys()):
        found_level = levels_by_address[level_address]
        levels_per_object_set[found_level.object_set_number].append(level_address)

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

        level_address = hex_int(level_address) - 9
        object_set_num = hex_int(object_set_no)

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
            list(
                map(
                    hex,
                    set(levels_per_object_set[object_set_num]).difference(levels[object_set_num]),
                )
            ),
        )

    return levels_per_object_set, levels_by_address
