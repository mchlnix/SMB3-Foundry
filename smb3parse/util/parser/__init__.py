"""Discover SMB3 levels by walking ROM pointers and jump destinations.

This module turns raw world-map level pointers, special per-world level slots,
and jump-object destinations into normalized records that higher-level tools can
inspect or persist. ``FoundLevelRecord`` captures one discovered reference
before parsing, while ``FoundLevel`` stores the merged result after the parser
has measured object and enemy data lengths and collected every origin that
reaches the same level address.

The main workflow starts in :func:`gen_levels_in_rom`, which enumerates worlds,
seeds discovery from :class:`smb3parse.levels.world_map.WorldMap`, follows jump
destinations through :class:`smb3parse.util.parser.cpu.NesCPU`, and finally
groups the results by object set for callers that need editor-facing or
validation-friendly summaries.

See Also
--------
smb3parse.levels.world_map.WorldMap
    Supplies world-map pointers and static world-specific level addresses.
smb3parse.levels.level_header.LevelHeader
    Decodes jump destinations from parsed level headers.
smb3parse.util.parser.cpu.NesCPU
    Emulates the ROM load path used to measure parsed level object data.
"""

import pathlib
import time
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Generator

from smb3parse.constants import (
    MUSHROOM_OBJECT_SET,
    OFFSET_SIZE,
    PLAINS_OBJECT_SET,
    SPADE_BONUS_OBJECT_SET,
    UNDERGROUND_OBJECT_SET,
    WORLD_MAP_OBJECT_SET,
)
from smb3parse.data_points import LevelPointerData
from smb3parse.levels import HEADER_LENGTH, WORLD_COUNT, WORLD_MAP_WARP_WORLD_INDEX
from smb3parse.levels.level_header import LevelHeader
from smb3parse.levels.world_map import WorldMap
from smb3parse.util import apply, hex_int
from smb3parse.util.parser.cpu import NesCPU
from smb3parse.util.rom import Rom

_DEFAULT_LEVEL_PARSING_MAX_STEPS = 1_000_000
"""On average it takes 35k steps to parse a stock level, longest was ~160k steps."""


@dataclass
class FoundLevel:
    """Store one discovered level together with every ROM origin that reaches it.

    The parser collapses repeated discoveries for the same level address into a
    single ``FoundLevel`` so later tools can reason about one canonical level
    entry while still preserving every pointer or jump that references it.
    Object and enemy lengths are filled in only after the level bytes have been
    parsed successfully, which lets callers distinguish between raw discovery
    metadata and measured serialized payload size.

    Attributes
    ----------
    level_offset_positions : list[int]
        ROM addresses whose level pointer bytes resolve to ``level_offset``.
    enemy_offset_positions : list[int]
        ROM addresses whose enemy pointer bytes resolve to ``enemy_offset``.
    world_number : int
        World used when this canonical level entry was first parsed.
    level_offset : int
        Absolute ROM address of the level header and object stream.
    enemy_offset : int
        Absolute ROM address of the enemy stream associated with the level.
    object_set_number : int
        Object-set bank required to interpret the level object bytes.
    object_data_length : int
        Serialized object-data length including the level header but excluding
        the trailing delimiter byte.
    enemy_data_length : int
        Serialized enemy-data length excluding its leading and trailing
        delimiter bytes.
    found_in_world : bool
        Whether a world-map pointer reaches this level directly.
    found_as_jump : bool
        Whether any discovered origin reaches this level through a jump object.
    is_world_specific : bool
        Whether the level came from a per-world special slot such as airships,
        toad houses, or coin ships.

    Notes
    -----
    Instances begin as one :class:`FoundLevelRecord` plus parsed data lengths,
    then accumulate extra pointer origins through :func:`_add_new_origin_to_level`.
    That split keeps jump discovery free to revisit the same level address
    without losing which ROM offsets still need to be rewritten together.

    See Also
    --------
    FoundLevelRecord
        Carries one unresolved origin before the level bytes have been parsed.
    """

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
        """Serialize the discovered level into the persistence payload shape.

        The parser uses this payload shape as the stable handoff between a live
        ROM scan and later cache, export, or rearrangement steps, so every
        origin list and provenance flag is preserved verbatim.

        Returns
        -------
        dict[str, list[int] | int | bool]
            Dictionary whose keys mirror the dataclass fields so cached level
            discovery results can be written without losing origin metadata.
        """
        ret_dict = vars(self)

        return ret_dict

    @staticmethod
    def from_dict(data: dict) -> "FoundLevel":
        """Rebuild a discovered level from persisted parser output.

        This method restores the exact canonical record shape used after
        discovery so later tooling can resume from cached parser output without
        re-walking world maps or jump chains.

        Parameters
        ----------
        data : dict
            Mapping previously produced by :meth:`to_dict`. Older payloads may
            still use ``is_generic``; this loader keeps those caches readable
            by translating that legacy field into ``is_world_specific``.

        Returns
        -------
        FoundLevel
            Reconstructed canonical level record ready for grouping, display,
            or further ROM updates.
        """
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
        """Promote a discovery record into a fully measured level result.

        This is the point where a raw pointer-origin record becomes a canonical
        parsed level entry: one origin is preserved, the active world context is
        attached, and the CPU-emulated load results become persistent length
        metadata for downstream ROM-edit workflows.

        Parameters
        ----------
        record : FoundLevelRecord
            Discovery origin that identified the level and enemy pointer bytes.
        world_num : int
            World being scanned when the parser successfully loaded the level.
        object_data_len : int
            Parsed object-stream length reported by the CPU loader.
        enemy_data_len : int
            Parsed enemy-stream length reported by the CPU loader.

        Returns
        -------
        FoundLevel
            Canonical level entry seeded with one origin and the measured ROM
            data lengths needed by later export and validation tools.
        """
        return FoundLevel(
            [record.level_address_offset],
            [record.enemy_address_offset],
            world_num,
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
    """Describe one unresolved origin that points at a level in ROM.

    ``FoundLevelRecord`` is the transient unit used while discovery is still
    exploring the ROM graph. Each record carries just enough state to move from
    one ROM reference to the next: where the level and enemy pointer bytes were
    found, which object set must be used to parse the destination, and which
    provenance flags the eventual merged :class:`FoundLevel` must preserve.

    Attributes
    ----------
    level_address : int
        Absolute ROM address of the discovered level header and object data.
    level_address_offset : int
        ROM location whose pointer bytes produced ``level_address``.
    enemy_address : int
        Absolute ROM address of the discovered enemy data.
    enemy_address_offset : int
        ROM location whose pointer bytes produced ``enemy_address``.
    object_set : int
        Object-set bank used when loading the destination level.
    found_in_world : bool, default=False
        Whether the origin came from a world-map level pointer.
    found_as_jump : bool, default=False
        Whether the origin came from a jump object in another parsed level.
    is_world_specific : bool, default=False
        Whether the origin came from a static per-world slot rather than a
        level pointer shared across worlds.

    Notes
    -----
    Records stay intentionally lightweight so discovery can create them from
    world-map pointers, static special-level slots, and jump destinations
    before the parser knows whether two origins eventually collapse onto the
    same canonical :class:`FoundLevel`.

    See Also
    --------
    FoundLevel
        Merged result object produced after a record has been parsed.
    """

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
        """Build a discovery record from decoded world-map pointer data.

        This adapter is the handoff between the world-map decoding layer and
        the ROM-parser traversal loop. It strips the richer ``LevelPointerData``
        object down to the exact address, object-set, and provenance fields
        that later steps reuse when they either parse the destination level,
        replace the record with a jump destination, or merge the origin into an
        already-known canonical level.

        Parameters
        ----------
        level_pointer : LevelPointerData
            World-map pointer payload that already exposes absolute level and
            enemy addresses together with the pointer-byte locations in ROM.
        from_world : bool
            Whether this origin should be marked as coming directly from a
            world-map pointer.
        from_jump : bool
            Whether this origin should be marked as coming from a jump chain.
        world_specific : bool
            Whether the pointed-to level belongs to a per-world special slot.

        Returns
        -------
        FoundLevelRecord
            Transient discovery record ready to seed parsing or to merge into
            an already-known :class:`FoundLevel`.

        Notes
        -----
        Discovery calls this helper immediately after
        :class:`LevelPointerData` has resolved one world-map slot into absolute
        ROM addresses. The resulting record keeps the exact pointer-byte
        origins together with the provenance flags that later jump-following
        and merge steps must preserve when several origins collapse onto one
        canonical :class:`FoundLevel`.
        """
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
    was_cancelled = False  # whether this generator was cancelled by the user from the outside

    # go through all worlds, except the warp world, to search for levels
    for world_num in range(1, WORLD_COUNT):
        levels_in_world = 0

        world = WorldMap.from_world_number(rom, world_num)

        # add all levels found in the world map via level pointers
        found_level_records: list[FoundLevelRecord] = [
            (FoundLevelRecord.from_level_pointer(lp, True, False, False)) for lp in world.level_pointers
        ]

        # add all the static levels (airship, etc.)
        _add_static_levels_for_world(world, found_level_records)

        # go through all found levels and check their jump destinations for more levels
        for record in found_level_records:
            if was_cancelled:
                break

            # this level was already found on a different level pointer or as a jump destination, only update the info
            if record.level_address in levels_by_address:
                found_level = levels_by_address[record.level_address]
                _add_new_origin_to_level(found_level, record)

                continue

            # ignore the special bonus mini games
            if record.object_set == SPADE_BONUS_OBJECT_SET:
                continue

            print(f"W{world.number}", hex(record.level_address), hex(record.enemy_address), record.object_set)

            # traverse Jump Destinations by following the offsets in the header, until finding a known level or dead end
            was_cancelled, levels_in_world = yield from _follow_jump_destinations(
                levels_by_address, levels_in_world, max_steps, record, rom, world
            )

    if was_cancelled:
        return defaultdict(list), dict()

    print(time.time() - start)

    levels_by_object_set = _sort_levels_by_object_set(levels_by_address)

    _print_levels_by_object_set(levels_by_address, levels_by_object_set)

    _print_missing_stock_levels(levels_by_object_set)

    return levels_by_object_set, levels_by_address


def _follow_jump_destinations(
    levels_by_address: dict[int, FoundLevel],
    levels_in_world: int,
    max_steps: int,
    record: FoundLevelRecord,
    rom: Rom,
    world: WorldMap,
):
    while True:
        levels_in_world += 1

        was_cancelled = yield world.number, levels_in_world

        if was_cancelled:
            break

        try:
            # emulate the level loading of the ROM to let it parse the level objects
            parsed_level = NesCPU(rom).load_from_address(
                record.object_set, record.level_address, record.enemy_address, max_steps
            )
        except ValueError as ve:
            print(ve)
            break

        found_level = FoundLevel.from_record(
            record, world.number, parsed_level.object_data_length, parsed_level.enemy_data_length
        )

        # add the newly found level to the list of known levels
        levels_by_address[record.level_address] = found_level

        # if there is no jump object in this level, we've reached a dead end
        if not parsed_level.has_jump():
            break

        cur_level_header = LevelHeader(rom, rom.read(record.level_address, HEADER_LENGTH))

        # no jump destination set, even though a jump object was found
        if cur_level_header.jump_level_offset == 0x0 or cur_level_header.jump_object_set_number == WORLD_MAP_OBJECT_SET:
            break

        # build record for new jump destination
        new_level_address_position = record.level_address
        new_level_address = cur_level_header.jump_level_address

        new_enemy_address_position = record.level_address + OFFSET_SIZE
        new_enemy_address = cur_level_header.jump_enemy_address

        object_set_number = cur_level_header.jump_object_set_number

        new_record = FoundLevelRecord(
            new_level_address,
            new_level_address_position,
            new_enemy_address,
            new_enemy_address_position,
            object_set_number,
        )

        new_record.found_as_jump = True

        # if we already know about this level, simply add this reference to it
        if new_level_address in levels_by_address:
            found_level = levels_by_address[new_level_address]

            _add_new_origin_to_level(found_level, new_record)
            break

        # replace the level record and start again
        record = new_record

        print("    ", hex(new_level_address), object_set_number)
    return was_cancelled, levels_in_world


def _sort_levels_by_object_set(levels_by_address: dict[int, FoundLevel]) -> defaultdict[int, list[int]]:
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
    """
    We want the FoundLevel object to keep a record of all the places in the Rom it is referenced. For example if more
    than one level uses it as their Jump Destination, or if more than one Level Pointer points to it.

    Therefore, add that information from the FoundLevelRecord to the given FoundLevel, including the type of reference
    it is.
    """
    assert record.level_address_offset not in found_level.level_offset_positions
    found_level.level_offset_positions.append(record.level_address_offset)

    assert record.enemy_address_offset not in found_level.enemy_offset_positions
    found_level.enemy_offset_positions.append(record.enemy_address_offset)

    found_level.found_in_world |= record.found_in_world
    found_level.found_as_jump |= record.found_as_jump
    found_level.is_world_specific |= record.is_world_specific


def _add_static_levels_for_world(world: WorldMap, level_records: list[FoundLevelRecord]):
    # add airship
    level_records.append(_airship_level_for_world(world))

    # add generic exit
    level_records.append(_generic_exit_level_for_world(world))

    # add big ? level
    level_records.append(_big_q_block_level_for_world(world))

    # add coin ship level
    level_records.append(_coin_ship_level_for_world(world))

    # add special/white toad house level
    level_records.append(_toad_warp_level_for_world(world))


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
