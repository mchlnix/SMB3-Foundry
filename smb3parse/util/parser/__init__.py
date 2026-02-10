import pathlib
import time
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Generator

from smb3parse.constants import OFFSET_SIZE
from smb3parse.data_points import LevelPointerData
from smb3parse.levels import HEADER_LENGTH, WORLD_COUNT, WORLD_MAP_WARP_WORLD_INDEX
from smb3parse.levels.level_header import LevelHeader
from smb3parse.levels.world_map import WorldMap
from smb3parse.objects.object_set import (
    MUSHROOM_OBJECT_SET,
    PLAINS_OBJECT_SET,
    SPADE_BONUS_OBJECT_SET,
    UNDERGROUND_OBJECT_SET,
    WORLD_MAP_OBJECT_SET,
)
from smb3parse.util import apply, hex_int
from smb3parse.util.parser.cpu import NesCPU
from smb3parse.util.rom import Rom

_DEFAULT_LEVEL_PARSING_MAX_STEPS = 1_000_000
"""On average it takes 35k steps to parse a stock level, longest was ~160k steps."""


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
    is_world_specific: bool

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
            data.get("is_world_specific", data.get("is_generic", False)),  # backwards compatible
        )

    @staticmethod
    def from_record(record: "FoundLevelRecord", world_num: int, object_data_len: int, enemy_data_len: int):
        return FoundLevel(
            [record.level_address_offset],
            [record.enemy_address_offset],
            world_num + 1,
            record.level_address,
            record.enemy_address,
            record.object_set,
            object_data_len,
            enemy_data_len,
            record.found_in_world,
            record.found_as_jump,
            record.is_world_specific,
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
    is_world_specific: bool = False

    @staticmethod
    def from_level_pointer(
        level_pointer: LevelPointerData,
        from_world: bool,
        from_jump: bool,
        world_specific: bool,
    ) -> "FoundLevelRecord":
        return FoundLevelRecord(
            level_pointer.level_address,
            level_pointer.level_offset_address,
            level_pointer.enemy_address,
            level_pointer.enemy_offset_address,
            level_pointer.object_set,
            from_world,
            from_jump,
            world_specific,
        )


def gen_levels_in_rom(
    rom: Rom, max_steps=_DEFAULT_LEVEL_PARSING_MAX_STEPS
) -> Generator[tuple[int, int], bool, tuple[dict, dict[int, FoundLevel]]]:
    levels_by_address: dict[int, FoundLevel] = {}

    start = time.time()

    for world_num in range(WORLD_COUNT - 1):
        levels_in_world = 0

        world = WorldMap.from_world_number(rom, world_num + 1)

        found_level_records = _add_static_levels_for_world(world)

        was_cancelled = False

        for record in found_level_records:
            if was_cancelled:
                return defaultdict(list), levels_by_address

            if record.level_address in levels_by_address:
                found_level = levels_by_address[record.level_address]
                _add_new_origin_to_level(found_level, record)

                continue

            if record.object_set == SPADE_BONUS_OBJECT_SET:
                continue

            print(f"W{world_num + 1}", hex(record.level_address), hex(record.enemy_address), record.object_set)

            # traverse Jump Destinations by following the offsets in the header
            while True:
                levels_in_world += 1

                was_cancelled = yield world.number, levels_in_world

                if was_cancelled:
                    break

                try:
                    parsed_level = NesCPU(rom).load_from_address(
                        record.object_set, record.level_address, record.enemy_address, max_steps
                    )
                except ValueError as ve:
                    print(ve)
                    break

                found_level = FoundLevel.from_record(
                    record, world_num, parsed_level.object_data_length, parsed_level.enemy_data_length
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

                # no jump destination set
                if header_of_old_level.jump_level_offset == 0x0 or object_set_number == WORLD_MAP_OBJECT_SET:
                    break

                new_record.found_as_jump = True

                if level_address in levels_by_address:
                    found_level = levels_by_address[level_address]

                    _add_new_origin_to_level(found_level, new_record)
                    break

                # set new record to old one to go along the chain of jumps
                record = new_record

                print("    ", hex(level_address), object_set_number)

    print(time.time() - start)

    levels_by_object_set = _sort_levels_by_object_set(levels_by_address)

    _print_levels_by_object_set(levels_by_address, levels_by_object_set)

    _print_missing_stock_levels(levels_by_object_set)

    return levels_by_object_set, levels_by_address


def _sort_levels_by_object_set(levels_by_address: dict[int, FoundLevel]) -> defaultdict[Any, list]:
    levels_by_object_set = defaultdict(list)

    for level_address in sorted(levels_by_address.keys()):
        found_level = levels_by_address[level_address]
        levels_by_object_set[found_level.object_set_number].append(level_address)
    return levels_by_object_set


def _print_levels_by_object_set(levels_by_address: dict[int, FoundLevel], levels_by_object_set: defaultdict[int, list]):
    total_level_count = 0

    for object_set_num, levels_addresses in sorted(levels_by_object_set.items()):
        total_level_count += len(levels_addresses)

        address_and_sources = [
            f"{hex(level_address).upper().replace('X', 'x')}/"
            f"{len(levels_by_address[level_address].level_offset_positions)}"
            for level_address in sorted(levels_addresses)
        ]
        print(object_set_num, ": ", len(levels_addresses), ", ".join(address_and_sources))

    print("---------------------", total_level_count, "------------------------")


def _print_missing_stock_levels(levels_by_object_set: defaultdict[Any, list]):
    """
    Check which of the known stock levels are missing in this particular ROM. Interesting with a stock ROM for testing.
    """
    root_dir = pathlib.Path(__file__).parent.parent.parent.parent

    stock_level_file = root_dir / "data" / "levels.dat"

    missing = 0
    missing_levels: dict[int, set[int]] = defaultdict(set)

    for line in stock_level_file.open("r").readlines():
        if not line:
            continue

        world_no, *_, level_address_str, _, object_set_no, _ = line.split(",")

        level_address = hex_int(level_address_str) - HEADER_LENGTH
        object_set_num = hex_int(object_set_no)

        if int(world_no) - 1 in [-1, WORLD_MAP_WARP_WORLD_INDEX]:
            continue

        missing_levels[object_set_num].add(level_address)

        if level_address not in levels_by_object_set[object_set_num]:
            missing += 1
            print(world_no, object_set_num, hex(level_address))

    print(missing, "stock levels are missing")

    for object_set_num in range(PLAINS_OBJECT_SET, UNDERGROUND_OBJECT_SET + 1):
        missing_by_object_set = set(levels_by_object_set[object_set_num]).difference(missing_levels[object_set_num])
        print(object_set_num, apply(hex, missing_by_object_set))


def _add_new_origin_to_level(found_level: FoundLevel, record: FoundLevelRecord):
    assert record.level_address_offset not in found_level.level_offset_positions
    found_level.level_offset_positions.append(record.level_address_offset)

    assert record.enemy_address_offset not in found_level.enemy_offset_positions
    found_level.enemy_offset_positions.append(record.enemy_address_offset)

    found_level.found_in_world |= record.found_in_world
    found_level.found_as_jump |= record.found_as_jump
    found_level.is_world_specific |= record.is_world_specific


def _add_static_levels_for_world(world: WorldMap) -> list[FoundLevelRecord]:
    found_level_records: list[FoundLevelRecord] = [
        (FoundLevelRecord.from_level_pointer(lp, True, False, False)) for lp in world.level_pointers
    ]

    # add airship
    found_level_records.append(_airship_level_for_world(world))

    # add generic exit
    found_level_records.append(_generic_exit_level_for_world(world))

    # add big ? level
    found_level_records.append(_big_q_block_level_for_world(world))

    # add coin ship level
    found_level_records.append(_coin_ship_level_for_world(world))

    # add special/white toad house level
    found_level_records.append(_toad_warp_level_for_world(world))

    return found_level_records


def _toad_warp_level_for_world(world: WorldMap) -> FoundLevelRecord:
    return FoundLevelRecord(
        world.data.toad_warp_level_address,
        world.data.toad_warp_level_offset_address,
        0x0,  # enemy item data is used directly, not as an offset
        world.data.toad_warp_item_address,
        MUSHROOM_OBJECT_SET,
        False,
        False,
        True,
    )


def _coin_ship_level_for_world(world: WorldMap) -> FoundLevelRecord:
    return FoundLevelRecord(
        world.data.coin_ship_level_address,
        world.data.coin_ship_level_offset_address,
        world.data.coin_ship_enemy_address,
        world.data.coin_ship_enemy_offset_address,
        world.data.coin_ship_level_object_set,
        False,
        False,
        True,
    )


def _big_q_block_level_for_world(world: WorldMap) -> FoundLevelRecord:
    return FoundLevelRecord(
        world.data.big_q_block_level_address,
        world.data.big_q_block_level_offset_address,
        world.data.big_q_block_enemy_address,
        world.data.big_q_block_enemy_offset_address,
        world.data.big_q_block_object_set,
        False,
        False,
        True,
    )


def _generic_exit_level_for_world(world: WorldMap) -> FoundLevelRecord:
    return FoundLevelRecord(
        world.data.generic_exit_level_address,
        world.data.generic_exit_level_offset_address,
        world.data.generic_exit_enemy_address,
        world.data.generic_exit_enemy_offset_address,
        world.data.generic_exit_object_set,
        False,
        False,
        True,
    )


def _airship_level_for_world(world: WorldMap) -> FoundLevelRecord:
    return FoundLevelRecord(
        world.data.airship_level_address,
        world.data.airship_level_offset_address,
        world.data.airship_enemy_address,
        world.data.airship_enemy_offset_address,
        world.data.airship_level_object_set,
        False,
        False,
        True,
    )
