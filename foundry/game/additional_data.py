"""Persist and reorganize editor-only metadata stored after the ROM bytes.

Foundry appends a small JSON payload after its ROM marker so it can remember
editor state that SMB3 itself does not store, such as discovered levels and
whether automatic level placement is enabled. This module defines both that
persisted metadata object and the working structures used when Foundry compacts
or rewrites level and enemy streams.

See Also
--------
foundry.game.File
    Saves and loads the trailing Foundry metadata block around the ROM bytes.
foundry.game.level.Level
    Consumes managed addresses and discovered-level metadata during editing.
foundry.gui.rom_settings.managed_levels_mixin
    User-facing workflow that enables or refreshes managed level positions.

Examples
--------
Foundry persists editor-only metadata next to the ROM and later uses it to run
managed save passes::

    additional_data = AdditionalData(rom)
    additional_data.managed_level_positions = True
    additional_data.found_levels = discovered_levels
"""

import json
from collections import defaultdict
from operator import attrgetter
from typing import TYPE_CHECKING

from foundry.game.level import (
    EMPTY_ENEMY_DATA,
    EMPTY_OBJECT_DATA,
    EnemyItemAddress,
    EnemyItemData,
    LevelAddress,
    ObjectData,
)
from smb3parse.constants import (
    BASE_OFFSET,
    ENEMY_DATA_BANK_INDEX,
    OFFSET_SIZE,
    PAGE_A000_OFFSET,
    Constants,
)
from smb3parse.levels import HEADER_LENGTH
from smb3parse.levels.level_header import LevelHeader
from smb3parse.util.parser import FoundLevel
from smb3parse.util.rom import PRG_BANK_SIZE, Rom

if TYPE_CHECKING:
    from foundry.game.level.Level import Level

_ENEMY_BANK_START = ENEMY_DATA_BANK_INDEX * PRG_BANK_SIZE + BASE_OFFSET

LEVEL_DATA_DELIMITER_COUNT = 1
ENEMY_DATA_DELIMITER_COUNT = 2


class AdditionalData:
    """Set of additional, foundry-specific data, meant to persist between invocations of the editor.
    Can be used to keep ROM specific decisions or settings, that have no place in the actual game data.

    The object is serialized after Foundry's ROM marker and tracks editor-only
    metadata such as discovered levels and whether Foundry owns level-data
    placement in the ROM.

    Parameters
    ----------
    rom : Rom
        ROM data source used for game data lookups.

    Attributes
    ----------
    found_levels : list[FoundLevel]
        Levels discovered in the ROM and their pointer locations.
    managed_level_positions : bool | None
        Whether Foundry should compact and rewrite level positions.
    needs_refresh : bool
        Whether discovered level metadata should be refreshed.
    rom : Rom
        ROM data source used for address and table lookups.
    """

    def __init__(self, rom: Rom):
        """Create empty Foundry metadata for a ROM.

        Parameters
        ----------
        rom : Rom
            ROM data source used for game data lookups.
        """
        self.rom = rom

        self.managed_level_positions: bool | None = None
        """
        If this is True, then the positions of the level data in the ROM is completely managed by the editor. The old
        way of remembering the position of a level, while editing, and manually opening it using this address will not
        work with this.
        """

        self.found_levels: list[FoundLevel] = []

        self.needs_refresh = False

    def __str__(self) -> str:
        """Serialize Foundry metadata to JSON.

        The resulting string is what ``ROM.save_to_file()`` appends after the
        Foundry marker, so it acts as the stable persistence format for
        editor-only metadata.


        Returns
        -------
        str
            JSON payload appended after Foundry's ROM marker.

        Examples
        --------
        The serialized payload captures editor-only state that Foundry restores
        on the next load::

            payload = str(additional_data)
            restored = AdditionalData.from_str(rom, payload)
        """
        return json.dumps(
            {
                "managed_level_positions": self.managed_level_positions,
                "found_levels": [found_level.to_dict() for found_level in self.found_levels],
                "needs_refresh": self.needs_refresh,
            }
        )

    @staticmethod
    def from_str(string_data: str, rom: Rom) -> "AdditionalData":
        """Deserialize Foundry metadata from JSON.

        This is the inverse of ``__str__`` and rebuilds the editor-only state
        that Foundry persists alongside the ROM bytes.


        Parameters
        ----------
        string_data : str
            JSON payload read after Foundry's ROM marker.
        rom : Rom
            ROM data source used for game data lookups.

        Returns
        -------
        'AdditionalData'
            Additional data populated from the serialized JSON string.
        """
        data_obj = AdditionalData(rom)

        data_dict = json.loads(string_data)

        data_obj.managed_level_positions = data_dict.get("managed_level_positions", None)
        data_obj.found_levels = [FoundLevel.from_dict(data) for data in data_dict.get("found_levels", [])]
        data_obj.needs_refresh = data_dict.get("needs_refresh", True)

        return data_obj

    def __bool__(self):
        """Report whether the ROM carries any editor-only metadata.

        This truthiness check is used when deciding whether Foundry should
        append its metadata block back to disk during ROM saves.

        Returns
        -------
        bool
            ``True`` when level management was decided or found levels exist.
        """
        return bool(self.managed_level_positions is not None or self.found_levels)

    def free_space_for_object_set(self, object_set_number: int):
        """Compute remaining object-data space in an object-set PRG bank.

        The calculation finds the last discovered level in the bank selected by
        the object set and reports bytes left before the PRG bank boundary.

        Parameters
        ----------
        object_set_number : int
            Object set number that selects graphics and object definitions.

        Returns
        -------
        int
            Remaining object data space for the object set.
        """
        prg_banks_by_object_set = self.rom.read(Constants.OFFSET_BY_OBJECT_SET_A000, 16)

        levels_by_bank: dict[int, list[FoundLevel]] = defaultdict(list)

        for level in self.found_levels:
            levels_by_bank[prg_banks_by_object_set[level.object_set_number]].append(
                MovableLevel.from_found_level(level)
            )

        last_level = levels_by_bank[prg_banks_by_object_set[object_set_number]][-1]

        free_space_start = last_level.level_offset + last_level.object_data_length + LEVEL_DATA_DELIMITER_COUNT

        free_space_left = PRG_BANK_SIZE - (free_space_start % PRG_BANK_SIZE)

        return free_space_left

    def free_space_for_enemies(self):
        """Compute remaining enemy-data space in the enemy PRG bank.

        The calculation starts after the latest discovered enemy data stream and
        accounts for the stream delimiter, mirroring the managed-layout save
        pass used by automatic level management.

        Returns
        -------
        int
            Remaining enemy data space for the level.
        """
        level_with_last_enemy_data = max(self.found_levels, key=attrgetter("enemy_offset"))

        end_of_enemy_data = (
            level_with_last_enemy_data.enemy_offset
            + level_with_last_enemy_data.enemy_data_length
            + ENEMY_DATA_DELIMITER_COUNT
        )

        # FIXME: when the level is not attached to the ROM yet, we have to reserve space for the delimiters, too
        return PRG_BANK_SIZE - (end_of_enemy_data % PRG_BANK_SIZE)

    def clear(self):
        """Discard Foundry-managed metadata before the next ROM save.

        Calling this removes the level-management decision, drops discovered
        levels, and strips the metadata block that Foundry would otherwise
        append after the ROM bytes during save. The next save therefore writes
        only game data unless a later refresh repopulates this editor-only
        state.
        """
        self.managed_level_positions = None
        self.found_levels.clear()


class MovableLevel(FoundLevel):
    """Wrap a found level while rearranging ROM data.

    ``LevelOrganizer`` needs a mutable working copy of each ``FoundLevel`` while
    compacting object and enemy streams. ``level_base`` points back to the
    persisted metadata record so final offsets can be synchronized.

    Attributes
    ----------
    level_base : FoundLevel
        Original discovered level metadata record.
    level_data : bytearray
        Header/object bytes being moved or saved.
    """

    level_data: bytearray
    level_base: FoundLevel

    @staticmethod
    def from_found_level(level: FoundLevel):
        """Create a movable working copy from discovered level metadata.

        The returned wrapper is the mutable record the organizer rewrites
        during compaction, while ``level_base`` still points at the original
        metadata entry that will receive the final addresses after the managed
        save pass finishes.


        Parameters
        ----------
        level : FoundLevel
            Discovered level metadata to wrap.

        Returns
        -------
        MovableLevel
            Working copy used during address rearrangement.
        """
        ret_level = MovableLevel([], [], 0, 0, 0, 0, 0, 0, False, False, False)

        ret_level.__dict__.update(vars(level))

        ret_level.level_base = level

        ret_level.level_data = bytearray()

        return ret_level

    def update_level_offset(self, value):
        """Update the original metadata level offset.


        Parameters
        ----------
        value : int
            New layout/header ROM address.
        """
        self.level_base.level_offset = value

    def update_enemy_offset(self, value):
        """Update the original metadata enemy offset.


        Parameters
        ----------
        value : int
            New enemy/item ROM address.
        """
        self.level_base.enemy_offset = value


class LevelOrganizer:
    """Compact managed level and enemy data inside the ROM.

    When Foundry manages level positions, saving a level can change object or
    enemy stream sizes. The organizer groups levels by PRG bank, generates new
    contiguous addresses, rewrites all recorded pointers, copies byte streams to
    their new locations, and records old-to-new address maps for jump updates.
    It is the save-time bridge between one edited ``Level`` instance and the
    wider managed ROM layout: after the level being saved grows or shrinks, this
    class repacks neighboring streams, rewrites pointers, and leaves both
    runtime ``Level`` objects and discovered metadata pointing at the same new
    compacted addresses.

    Parameters
    ----------
    rom : 'Rom'
        ROM data source used for game data lookups.
    levels : list[FoundLevel]
        Discovered level metadata records to rearrange.
    level_to_save : ObjectData, optional
        Replacement header/object stream for one level.
    enemies_to_save : EnemyItemData, optional
        Replacement enemy/item stream for one level.

    Attributes
    ----------
    levels : list[FoundLevel]
        Discovered level metadata records being managed.
    levels_by_bank : dict[int, list[MovableLevel]]
        Working levels grouped by object-data PRG bank during repacking.
    next_area_enemies : EnemyItemAddress
        Rewritten enemy address prepared for the saved level's next-area header.
    next_area_objects : LevelAddress
        Rewritten object address prepared for the saved level's next-area header.
    enemies_to_save : EnemyItemData
        Enemy stream that should replace one existing stream during repacking.
    level_to_save : ObjectData
        Level stream that should replace one existing stream during repacking.
    old_enemy_address_to_new : dict[EnemyItemAddress, EnemyItemAddress]
        Mapping from previous enemy stream address to its compacted address.
    old_level_address_to_new : dict[LevelAddress, LevelAddress]
        Mapping from previous level stream address to its compacted address.
    rom : Rom
        ROM being rewritten during the managed save pass.

    Notes
    -----
    The organizer's working state is built in phases: levels are grouped by
    bank, new addresses are assigned, byte streams are copied, and only then do
    pointer-fixup helpers consume the old-to-new maps to synchronize metadata.
    The net result is that a normal ``Level`` save can hand off to this class,
    let managed addresses shift underneath it, and then reconnect the edited
    level plus its jump metadata to the new compacted layout.
    Git history around automatic level management shows why this code was split
    out: rearrangement had to become testable, reusable, and separate from the
    normal save path. ``LevelOrganizer`` is that orchestration layer for the
    managed-save workflow.

    See Also
    --------
    AdditionalData
        Owns the discovered level metadata that feeds this organizer.
    MovableLevel
        Wraps one discovered level with mutable save-pass state.

    Examples
    --------
    Managed save code hands the organizer a discovered level table plus one
    replacement stream, then lets it repack addresses before the level is
    reopened::

        organizer = LevelOrganizer(rom, levels, level_to_save, enemies_to_save)
        organizer.rearrange_levels()
        organizer.rearrange_enemies()

    The organizer is also the bridge from discovered metadata to rewritten
    pointer tables::

        sorted_levels = organizer._sort_levels_by_enemy_address()
        organizer._generate_new_enemy_addresses(sorted_levels)
    """

    def __init__(
        self,
        rom: "Rom",
        levels: list[FoundLevel],
        level_to_save: ObjectData = EMPTY_OBJECT_DATA,
        enemies_to_save: EnemyItemData = EMPTY_ENEMY_DATA,
    ):
        """Create an organizer for a managed-level save pass.

        The organizer receives the discovered metadata snapshot plus any
        replacement object or enemy stream for the level being saved, then uses
        that combined state to compact ROM layout and rewrite pointers.


        Parameters
        ----------
        rom : 'Rom'
            ROM data source used for game data lookups.
        levels : list[FoundLevel]
            Levels consumed by the operation.
        level_to_save : ObjectData, optional
            Replacement header/object stream for one level.
        enemies_to_save : EnemyItemData, optional
            Replacement enemy/item stream for one level.
        """
        self.rom = rom

        self.levels = levels
        self.levels_by_bank: dict[int, list[MovableLevel]] = {}

        self.level_to_save = level_to_save
        self.enemies_to_save = enemies_to_save

        self.old_level_address_to_new: dict[LevelAddress, LevelAddress] = {}
        self.old_enemy_address_to_new: dict[EnemyItemAddress, EnemyItemAddress] = {}

    def update_level_info(self, level: "Level"):
        """Syncs changes made to a 'normal' Level to its Found Level and back, after rearranging Levels based on the
        changes.

        This keeps managed-level metadata synchronized after a level is moved or rewritten.

        Parameters
        ----------
        level : 'Level'
            Level whose metadata and jump destination should be synchronized.
        """
        # 1. Update the level and enemy data sizes of the current level
        self._update_level_sizes(level)

        # 2. Rearrange all levels based on new sizes
        self.rearrange_levels()
        self.rearrange_enemies()

        # 3. Update level and enemy addresses after rearranging
        self._update_level_addresses(level)

        # 4. Update jump destination addresses after rearranging
        self._update_jump_destination(level)

    def _get_found_level(self, level: "Level"):
        """Resolve the discovered metadata record for a ROM-attached level.

        Managed saves use this lookup to bridge from the live ``Level`` object
        back to the persisted ``FoundLevel`` metadata entry that owns pointer
        positions and serialized lengths.


        Parameters
        ----------
        level : 'Level'
            Level whose current header address should be found.

        Returns
        -------
        FoundLevel
            Metadata record matching the level's header address.

        Raises
        ------
        LookupError
            If the level's metadata record cannot be found.
        ValueError
            If the input data or current state is invalid.
        """
        if not level.attached_to_rom:
            raise ValueError("This level is not attached to the ROM. Please place it somewhere on a world map.")

        current_level = self._found_level_from_address(level.header_offset)

        if current_level is None:
            raise LookupError(f"Current Level {level.header_offset:x} could not be found in ROM. Attach it first.")

        return current_level

    def _found_level_from_address(self, level_address: int) -> FoundLevel | None:
        """Look up discovered level metadata by layout address.

        Managed save paths use this helper whenever they need to translate a
        live ROM address back into the metadata record that tracks pointer
        positions and stream lengths.


        Parameters
        ----------
        level_address : int
            ROM address of the level layout data.

        Returns
        -------
        FoundLevel | None
            Found level matching the ROM address, if one exists.
        """
        try:
            return next(filter(lambda lvl: lvl.level_offset == level_address, self.levels))

        except StopIteration:
            return None

    def _update_level_sizes(self, level: "Level"):
        """Given Level might have changed in size, so this needs to be synced with its Found Level, before rearranging.

        Object data length includes the header but excludes the object-stream
        delimiter. Enemy data length excludes enemy delimiters.

        Parameters
        ----------
        level : 'Level'
            Level whose current serialized sizes should be copied to metadata.
        """

        found_level = self._get_found_level(level)

        found_level.object_data_length = HEADER_LENGTH + level.current_object_size()
        found_level.enemy_data_length = level.current_enemies_size()

    def _update_level_addresses(self, level: "Level"):
        """After rearranging levels, the addresses for this normal Level might have changed, so update them.

        The level object receives the compacted addresses from the metadata
        maps generated during rearrangement.

        Parameters
        ----------
        level : 'Level'
            Level whose ROM addresses should be updated.
        """

        found_level = self._get_found_level(level)

        assert found_level.level_offset in self.old_level_address_to_new, (
            hex(found_level.level_offset),
            self.old_level_address_to_new,
        )
        assert found_level.enemy_offset in self.old_enemy_address_to_new

        found_level.level_offset = self.old_level_address_to_new[found_level.level_offset]
        found_level.enemy_offset = self.old_enemy_address_to_new[found_level.enemy_offset]

        level.set_addresses(found_level.level_offset, found_level.enemy_offset)

    def _update_jump_destination(self, level: "Level"):
        """Refresh found-level links for a level's next-area pointer.


        Parameters
        ----------
        level : 'Level'
            Level whose next-area metadata links should be refreshed.
        """
        self._disconnect_old_jump_destination(level)
        self._connect_new_jump_destination_to_level(level)

    def _disconnect_old_jump_destination(self, level: "Level"):
        """Find whatever Found Levels think they are the given Levels Jump Destinations and disconnect them.

        Pointer-position lists are metadata only; this removes stale references
        before the level's current jump destination is connected.

        Parameters
        ----------
        level : 'Level'
            Level whose previous next-area links should be removed.
        """

        jump_level_offset_address = level.header_offset
        jump_enemy_offset_address = level.header_offset + OFFSET_SIZE

        for found_level in self.levels:
            if jump_level_offset_address in found_level.level_offset_positions:
                found_level.level_offset_positions.remove(jump_level_offset_address)

            if jump_enemy_offset_address in found_level.enemy_offset_positions:
                found_level.enemy_offset_positions.remove(jump_enemy_offset_address)

    def _connect_new_jump_destination_to_level(self, level: "Level"):
        """Find the Found Level for the given Levels Jump Destination and connect them together.

        The destination must point at a known managed level unless both jump
        offsets are explicitly zero. Successful lookup updates the destination
        metadata so later address compaction can rewrite the source level's
        next-area pointers correctly, instead of leaving the managed save pass
        with stale links to pre-compaction addresses.

        Parameters
        ----------
        level : 'Level'
            Level whose current next-area destination should be linked.

        Raises
        ------
        LookupError
            If the jump destination does not resolve to known managed metadata.
        """

        if level.header.jump_level_offset == level.header.jump_enemy_offset == 0x00:
            # Level Jump Destination is explicitly not set, so don't bother keeping track
            return

        if level.header.jump_level_offset and level.header.jump_level_address not in self.old_level_address_to_new:
            raise LookupError(
                f"Jump Destination Level Address in Header '0x{level.header.jump_level_address:X}' does not point to"
                " any known level. Set both to 0x0000 to disable this check."
            )
        if level.header.jump_enemy_offset and level.header.jump_enemy_address not in self.old_enemy_address_to_new:
            raise LookupError(
                f"Jump Destination Enemy Address in Header '0x{level.header.jump_enemy_address:X}' does not point to"
                " any known enemy data group. Set both to 0x0000 to disable this check."
            )

        jump_destination_found_level = self._found_level_from_address(level.header.jump_level_address)

        if jump_destination_found_level is None:
            raise LookupError(f"Jump Level Destination {level.header.jump_level_address:x} could not be found in ROM.")

        jump_destination_found_level.level_offset_positions.append(level.header_offset)
        jump_destination_found_level.enemy_offset_positions.append(level.header_offset + OFFSET_SIZE)

        if level.header.jump_level_offset != 0x0:
            self.next_area_objects = self.old_level_address_to_new[level.header.jump_level_address]

        if level.header.jump_enemy_offset != 0x0:
            self.next_area_enemies = self.old_enemy_address_to_new[level.header.jump_enemy_address]

    def rearrange_levels(self):
        # 0.1 Sort Levels by bank
        """Compact object streams and rewrite level pointers.

        Levels are grouped by object-set PRG bank so compaction never crosses
        bank boundaries. The method is the object-data half of the managed-save
        pipeline: inject replacement bytes, compute compacted addresses, patch
        pointers, and finally copy the streams.
        """
        self._separate_levels_by_banks()

        # 0.2 If a level is supposed to be saved, put the data of it into the movable level it is associated with
        found_save_level = self._inject_level_to_be_saved()

        # 1. Sort levels by their level address
        self._sort_levels_by_level_address()

        # 2. Generate new level addresses based on the old ones and the level sizes
        self._generate_new_level_addresses()

        # we might have to update the pointers in the header of the level we need to save
        if self.level_to_save != EMPTY_OBJECT_DATA:
            self._update_jump_address_for_saved_level(found_save_level)

        # 3. Go through all levels and update their level position pointers, with the new addresses
        self._update_level_and_enemy_pointers()

        # 4. Write level data to new position in bank
        self._copy_level_data_to_new_addresses()

    def _copy_level_data_to_new_addresses(self):
        """Copy each level object stream to its compacted address.

        Existing bytes are read lazily unless a replacement stream was injected
        for the level being saved.
        """
        for levels in self.levels_by_bank.values():
            # 4.1 Get level data from old position
            for level in levels:
                if not level.level_data:
                    level.level_data = self.rom.read(
                        level.level_offset,
                        level.object_data_length + LEVEL_DATA_DELIMITER_COUNT,
                    )

            # 4.2 Save level data to new position
            for level in levels:
                new_level_offset = self.old_level_address_to_new[level.level_offset]

                level.update_level_offset(new_level_offset)

                self.rom.write(new_level_offset, level.level_data)

    def _update_level_address_at_level_pointers(self, level, object_set_offset):
        """Rewrite all object-data pointers that target a moved level.

        SMB3 stores object pointers relative to the object-set page, so each
        pointer write converts the compacted absolute address back into the
        encoded form expected by the ROM as the managed-save pass rewrites
        pointer-bearing levels in place.


        Parameters
        ----------
        level : MovableLevel
            Level whose pointer positions should be rewritten.
        object_set_offset : int
            Object-set base offset used by SMB3 pointer encoding.
        """
        for position in level.level_offset_positions:
            self.rom.write_little_endian(
                position,
                self.old_level_address_to_new[level.level_offset] - object_set_offset,
            )

    def _update_level_and_enemy_address_pointers(self, level):
        """Update stored pointer-position metadata after compaction.

        Pointer positions can move when the level that contains a pointer moves,
        so the original ``FoundLevel`` metadata must be rewritten too.

        Parameters
        ----------
        level : MovableLevel
            Working level whose base metadata should be updated.
        """
        level.level_base.level_offset_positions = [
            self.old_level_address_to_new.get(position, position) for position in level.level_offset_positions
        ]
        level.level_base.enemy_offset_positions = [
            self.old_level_address_to_new.get(position - OFFSET_SIZE, position - OFFSET_SIZE)
            + ENEMY_DATA_DELIMITER_COUNT
            for position in level.enemy_offset_positions
        ]

    def _update_jump_address_for_saved_level(self, found_save_level: MovableLevel | None):
        """Update a saved level's embedded next-area address.

        If the replacement level stream contains a jump destination that also
        moved during compaction, its header bytes are patched before writing.

        Parameters
        ----------
        found_save_level : MovableLevel | None
            Working level containing replacement bytes, if one was injected.
        """
        if found_save_level is None:
            return

        header = LevelHeader(self.rom, found_save_level.level_data[:HEADER_LENGTH])

        if header.jump_level_address in self.old_level_address_to_new:
            header.jump_level_address = self.old_level_address_to_new[header.jump_level_address]

        found_save_level.level_data[:HEADER_LENGTH] = header.data

    def _update_level_and_enemy_pointers(self):
        """Rewrite level and enemy pointers for compacted addresses.

        Object-data pointers are encoded relative to the object-set page, while
        enemy pointers are encoded relative to the ROM base.
        """
        for bank_index, levels in self.levels_by_bank.items():
            object_set_offset = BASE_OFFSET + bank_index * PRG_BANK_SIZE - PAGE_A000_OFFSET

            # 3.1. Write new addresses in old positions, before actually moving the levels to the new position
            for level in levels:
                self._update_level_address_at_level_pointers(level, object_set_offset)

                self._update_level_and_enemy_address_pointers(level)

    def _generate_new_level_addresses(self):
        """Generate compacted object-stream addresses within each bank.

        The first level in each bank keeps its address; following levels are
        packed immediately after the previous stream and its delimiter.
        """
        self.old_level_address_to_new.clear()

        for levels in self.levels_by_bank.values():
            # 1. Take the first one as the bank start
            # FIXME: Figure out bank start on initial parsing and save that in additional data
            first_level = levels[0]

            new_level_start = first_level.level_offset

            # 2. Put them into a dictionary from old address to new address
            for level in levels:
                self.old_level_address_to_new[level.level_offset] = new_level_start
                new_level_start += (
                    level.object_data_length + LEVEL_DATA_DELIMITER_COUNT
                )  # one extra byte for the FF delimiter at the end

    def _sort_levels_by_level_address(self):
        """Sort working levels by object-stream address inside each bank."""
        for levels in self.levels_by_bank.values():
            levels.sort(key=attrgetter("level_offset"))

    def _inject_level_to_be_saved(self) -> MovableLevel | None:
        """Attach replacement object bytes to the matching working level.

        The injected stream includes the terminator, but metadata lengths store
        only the bytes before the delimiter. This is how the live level being
        saved participates in compaction without first being written back to its
        old ROM address.

        Returns
        -------
        MovableLevel | None
            Working level that received replacement bytes, if any.
        """
        if self.level_to_save is EMPTY_OBJECT_DATA:
            return None

        save_level_address, save_level_data = self.level_to_save

        for levels in self.levels_by_bank.values():
            for level in levels:
                if level.level_offset != save_level_address:
                    continue

                found_save_level = level
                found_save_level.level_data = save_level_data
                found_save_level.object_data_length = (
                    len(save_level_data) - LEVEL_DATA_DELIMITER_COUNT
                )  # ignore delimiter here

                return found_save_level

        return None

    def _separate_levels_by_banks(self):
        """Group discovered levels by object-data PRG bank.

        SMB3 selects object-data banks by object set, so compaction must be
        performed independently per bank.
        """
        prg_banks_by_object_set = self.rom.read(Constants.OFFSET_BY_OBJECT_SET_A000, 16)
        self.levels_by_bank = defaultdict(list)

        for level in self.levels:
            self.levels_by_bank[prg_banks_by_object_set[level.object_set_number]].append(
                MovableLevel.from_found_level(level)
            )

    def rearrange_enemies(self):
        # 1. Sort levels based on their enemy offset (filter out enemy offsets, that aren't real/mean something else)
        """Compact enemy streams and rewrite enemy pointers.

        Enemy data lives in a separate bank and may be shared by multiple
        levels, so duplicate enemy offsets are copied once and mapped to the
        same new address.
        """
        sorted_levels = self._sort_levels_by_enemy_address()

        # 1.1 If a level is supposed to be saved, put the data of it into the movable level
        self._update_enemy_data_length_in_levels(sorted_levels)

        # 2. Set the start of the enemy data bank and go through the rest of the levels and adjust the enemy offsets to
        #    leave no empty space
        self._generate_new_enemy_addresses(sorted_levels)

        # 3. Finally, write the enemy data to their new positions
        # 3.1 Get enemy data from old position
        old_enemy_data_sets = self._collect_enemy_data_from_current_addresses(sorted_levels)

        # 3.2 Save enemy data to new position
        self._update_enemy_address_and_copy_data(old_enemy_data_sets, sorted_levels)

    def _update_enemy_address_and_copy_data(self, old_enemy_data_sets, sorted_levels):
        """Copy enemy streams to compacted addresses.

        Shared enemy streams are written once even if multiple levels reference
        the same old enemy address. The method also updates each level's enemy
        offset to the compacted address chosen during the save pass.

        Parameters
        ----------
        old_enemy_data_sets : dict[EnemyItemAddress, bytearray]
            Enemy bytes collected from old addresses or the replacement stream.
        sorted_levels : list[FoundLevel]
            Levels sorted by enemy address.
        """
        already_copied = []

        for level in sorted_levels:
            old_enemy_data = old_enemy_data_sets[level.enemy_offset]
            level.enemy_offset = self.old_enemy_address_to_new[level.enemy_offset]

            if level.enemy_offset in already_copied:
                continue

            self.rom.write(level.enemy_offset, old_enemy_data)

    def _collect_enemy_data_from_current_addresses(self, sorted_levels) -> dict[EnemyItemAddress, bytearray]:
        """Read enemy streams before rewriting addresses.

        Existing streams are read from ROM. The replacement enemy stream, when
        present, overrides the bytes collected for its address so the save pass
        copies the edited stream instead of stale ROM data.

        Parameters
        ----------
        sorted_levels : list[FoundLevel]
            Levels sorted by enemy address.

        Returns
        -------
        dict[EnemyItemAddress, bytearray]
            The enemy data from current addresses.
        """
        old_enemy_data_sets = {
            level.enemy_offset: self.rom.read(level.enemy_offset, level.enemy_data_length + ENEMY_DATA_DELIMITER_COUNT)
            for level in sorted_levels
        }

        if self.enemies_to_save is not EMPTY_ENEMY_DATA:
            save_enemy_address, save_enemy_data = self.enemies_to_save
            old_enemy_data_sets[save_enemy_address] = save_enemy_data

        return old_enemy_data_sets

    def _generate_new_enemy_addresses(self, sorted_levels):
        """Generate compacted enemy stream addresses and rewrite pointers.

        Duplicate old enemy addresses reuse the first generated address so
        shared enemy data remains shared after compaction.

        Parameters
        ----------
        sorted_levels : list[FoundLevel]
            Levels sorted by enemy address.
        """
        last_enemy_end = _ENEMY_BANK_START

        self.old_enemy_address_to_new.clear()

        for level in sorted_levels:
            # some levels share enemies, so we don't count them again, otherwise we copy them into memory multiple times
            was_duplicate = level.enemy_offset in self.old_enemy_address_to_new

            if not was_duplicate:
                self.old_enemy_address_to_new[level.enemy_offset] = last_enemy_end

            for position in level.enemy_offset_positions:
                self.rom.write_little_endian(
                    position,
                    self.old_enemy_address_to_new[level.enemy_offset] - BASE_OFFSET,
                )

            if was_duplicate:
                continue

            last_enemy_end += level.enemy_data_length + ENEMY_DATA_DELIMITER_COUNT

    def _update_enemy_data_length_in_levels(self, sorted_levels):
        """Update metadata length for the replacement enemy stream.

        Metadata lengths exclude delimiter bytes, while serialized streams
        include them.

        Parameters
        ----------
        sorted_levels : list[FoundLevel]
            Levels sorted by enemy address.
        """
        save_enemy_address, save_enemy_data = self.enemies_to_save

        for level in filter(lambda level_: level_.enemy_offset == save_enemy_address, sorted_levels):
            level.enemy_data_length = (
                len(save_enemy_data) - ENEMY_DATA_DELIMITER_COUNT
            )  # do not account for delimiters here

    def _sort_levels_by_enemy_address(self):
        """Sort levels with ROM-backed enemy data by enemy address.

        Managed enemy compaction ignores pseudo-addresses and other sentinel
        values so only real enemy streams participate in the rewritten layout
        and address generation step before new compacted enemy addresses are
        assigned. The returned list is the exact sequence that
        ``rearrange_enemies`` hands to ``_update_enemy_data_length_in_levels``,
        ``_generate_new_enemy_addresses``, and the later copy and pointer-write
        helpers, so every later compaction step can treat enemy streams as one
        contiguous bank-local layout instead of reasoning about levels in
        discovery order. In data-flow terms, this method is the non-mutating
        ordering gate in the enemy-save pipeline: it filters the organizer's
        full level set down to real enemy streams, orders them, and returns the
        sequence the rest of the relocation pass consumes.

        Returns
        -------
        list[FoundLevel]
            Levels sorted by enemy data address.

        Examples
        --------
        Enemy compaction uses the returned order as the first step in address
        regeneration::

            sorted_levels = organizer._sort_levels_by_enemy_address()
            organizer._generate_new_enemy_addresses(sorted_levels)
        """
        return sorted(
            filter(lambda lvl: lvl.enemy_offset >= _ENEMY_BANK_START, self.levels),
            key=attrgetter("enemy_offset"),
        )
