import json
from collections import defaultdict
from operator import attrgetter

from foundry.game.level import (
    EMPTY_ENEMY_DATA,
    EMPTY_OBJECT_DATA,
    EnemyItemAddress,
    EnemyItemData,
    LevelAddress,
    ObjectData,
)
from smb3parse import PAGE_A000_ByTileset
from smb3parse.constants import BASE_OFFSET, ENEMY_DATA_BANK_INDEX, OFFSET_SIZE, PAGE_A000_OFFSET
from smb3parse.levels.level_header import LevelHeader
from smb3parse.util.parser import FoundLevel
from smb3parse.util.rom import PRG_BANK_SIZE, Rom


_ENEMY_BANK_START = ENEMY_DATA_BANK_INDEX * PRG_BANK_SIZE + BASE_OFFSET

LEVEL_DATA_DELIMITER_COUNT = 1
ENEMY_DATA_DELIMITER_COUNT = 2


class AdditionalData:
    """
    Set of additional, foundry specific data, meant to persist between invocations of the editor. Can be used to keep
    ROM specific decisions or settings, that have no place in the actual game data.
    """

    def __init__(self, rom: Rom):
        self.rom = rom

        self.managed_level_positions: bool | None = None
        """
        If this is True, then the positions of the level data in the ROM is completely managed by the editor. The old
        way of remembering the position of a level, while editing, and manually opening it using this address will not
        work with this.
        """

        self.found_level_information: list[FoundLevel] = []

    def __str__(self) -> str:
        return json.dumps(
            {
                "managed_level_positions": self.managed_level_positions,
                "found_level_information": [found_level.to_dict() for found_level in self.found_level_information],
            }
        )

    @staticmethod
    def from_str(string_data: str, rom: Rom) -> "AdditionalData":
        data_obj = AdditionalData(rom)

        data_dict = json.loads(string_data)

        data_obj.managed_level_positions = data_dict.get("managed_level_positions", None)
        data_obj.found_level_information = [
            FoundLevel.from_dict(data) for data in data_dict.get("found_level_information", [])
        ]

        return data_obj

    def __bool__(self):
        return bool(self.managed_level_positions is not None or self.found_level_information)

    def free_space_for_object_set(self, object_set_number: int):
        prg_banks_by_object_set = self.rom.read(PAGE_A000_ByTileset, 16)

        levels_by_bank: dict[int, list[FoundLevel]] = defaultdict(list)

        for level in self.found_level_information:
            levels_by_bank[prg_banks_by_object_set[level.object_set_number]].append(
                MovableLevel.from_found_level(level)
            )

        last_level = levels_by_bank[prg_banks_by_object_set[object_set_number]][-1]

        free_space_start = last_level.level_offset + last_level.object_data_length + LEVEL_DATA_DELIMITER_COUNT

        free_space_left = PRG_BANK_SIZE - (free_space_start % PRG_BANK_SIZE)

        return free_space_left

    def free_space_for_enemies(self):
        level_with_last_enemy_data = max(self.found_level_information, key=attrgetter("enemy_offset"))

        end_of_enemy_data = (
            level_with_last_enemy_data.enemy_offset
            + level_with_last_enemy_data.enemy_data_length
            + ENEMY_DATA_DELIMITER_COUNT
        )

        # FIXME: when the level is not attached to the ROM yet, we have to reserve space for the delimiters, too
        return PRG_BANK_SIZE - (end_of_enemy_data % PRG_BANK_SIZE)

    def clear(self):
        self.managed_level_positions = None
        self.found_level_information.clear()


class MovableLevel(FoundLevel):
    level_data: bytearray
    level_base: FoundLevel

    @staticmethod
    def from_found_level(level: FoundLevel):
        ret_level = MovableLevel([], [], 0, 0, 0, 0, 0, 0, False, False, False)

        ret_level.__dict__.update(vars(level))

        ret_level.level_base = level

        ret_level.level_data = bytearray()

        return ret_level

    def update_level_offset(self, value):
        self.level_base.level_offset = value

    def update_enemy_offset(self, value):
        self.level_base.enemy_offset = value


class LevelOrganizer:
    def __init__(
        self,
        rom: "Rom",
        levels: list[FoundLevel],
        level_to_save: ObjectData = EMPTY_OBJECT_DATA,
        enemies_to_save: EnemyItemData = EMPTY_ENEMY_DATA,
    ):
        self.rom = rom

        self.levels = levels
        self.levels_by_bank: dict[int, list[MovableLevel]] = {}

        self.level_to_save = level_to_save
        self.enemies_to_save = enemies_to_save

        self.old_level_address_to_new: dict[LevelAddress, LevelAddress] = {}
        self.old_enemy_address_to_new: dict[EnemyItemAddress, EnemyItemAddress] = {}

    def rearrange_levels(self):
        # 0.1 Sort Levels by bank
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
        for levels in self.levels_by_bank.values():
            # 4.1 Get level data from old position
            for level in levels:
                if not level.level_data:
                    level.level_data = self.rom.read(
                        level.level_offset, level.object_data_length + LEVEL_DATA_DELIMITER_COUNT
                    )

            # 4.2 Save level data to new position
            for level in levels:
                new_level_offset = self.old_level_address_to_new[level.level_offset]

                level.update_level_offset(new_level_offset)

                self.rom.write(new_level_offset, level.level_data)

    def _update_level_address_at_level_pointers(self, level, object_set_offset):
        for position in level.level_offset_positions:
            self.rom.write_little_endian(
                position, self.old_level_address_to_new[level.level_offset] - object_set_offset
            )

    def _update_level_and_enemy_address_pointers(self, level):
        level.level_base.level_offset_positions = [
            self.old_level_address_to_new.get(position, position) for position in level.level_offset_positions
        ]
        level.level_base.enemy_offset_positions = [
            self.old_level_address_to_new.get(position - OFFSET_SIZE, position - OFFSET_SIZE)
            + ENEMY_DATA_DELIMITER_COUNT
            for position in level.enemy_offset_positions
        ]

    def _update_jump_address_for_saved_level(self, found_save_level: MovableLevel | None):
        if found_save_level is None:
            return

        header = LevelHeader(self.rom, found_save_level.level_data[:9], found_save_level.object_set_number)

        if header.jump_level_address in self.old_level_address_to_new:
            header.jump_level_address = self.old_level_address_to_new[header.jump_level_address]

        found_save_level.level_data[:9] = header.data

    def _update_level_and_enemy_pointers(self):
        for bank_index, levels in self.levels_by_bank.items():
            object_set_offset = BASE_OFFSET + bank_index * PRG_BANK_SIZE - PAGE_A000_OFFSET

            # 3.1. Write new addresses in old positions, before actually moving the levels to the new position
            for level in levels:
                self._update_level_address_at_level_pointers(level, object_set_offset)

                self._update_level_and_enemy_address_pointers(level)

    def _generate_new_level_addresses(self):
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
        for levels in self.levels_by_bank.values():
            levels.sort(key=attrgetter("level_offset"))

    def _inject_level_to_be_saved(self) -> MovableLevel | None:
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
        prg_banks_by_object_set = self.rom.read(PAGE_A000_ByTileset, 16)
        self.levels_by_bank = defaultdict(list)

        for level in self.levels:
            self.levels_by_bank[prg_banks_by_object_set[level.object_set_number]].append(
                MovableLevel.from_found_level(level)
            )

    def rearrange_enemies(self) -> dict[EnemyItemAddress, EnemyItemAddress]:
        # 1. Sort levels based on their enemy offset (filter out enemy offsets, that aren't real/mean something else)
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

        return self.old_enemy_address_to_new

    def _update_enemy_address_and_copy_data(self, old_enemy_data_sets, sorted_levels):
        already_copied = []

        for level in sorted_levels:
            old_enemy_data = old_enemy_data_sets[level.enemy_offset]
            level.enemy_offset = self.old_enemy_address_to_new[level.enemy_offset]

            if level.enemy_offset in already_copied:
                continue

            self.rom.write(level.enemy_offset, old_enemy_data)

    def _collect_enemy_data_from_current_addresses(self, sorted_levels) -> dict[EnemyItemAddress, bytearray]:
        old_enemy_data_sets = {
            level.enemy_offset: self.rom.read(level.enemy_offset, level.enemy_data_length + ENEMY_DATA_DELIMITER_COUNT)
            for level in sorted_levels
        }

        if self.enemies_to_save is not EMPTY_ENEMY_DATA:
            save_enemy_address, save_enemy_data = self.enemies_to_save
            old_enemy_data_sets[save_enemy_address] = save_enemy_data

        return old_enemy_data_sets

    def _generate_new_enemy_addresses(self, sorted_levels):
        last_enemy_end = _ENEMY_BANK_START

        self.old_enemy_address_to_new.clear()

        for level in sorted_levels:
            # some levels share enemies, so we don't count them again, otherwise we copy them into memory multiple times
            was_duplicate = level.enemy_offset in self.old_enemy_address_to_new

            if not was_duplicate:
                self.old_enemy_address_to_new[level.enemy_offset] = last_enemy_end

            for position in level.enemy_offset_positions:
                self.rom.write_little_endian(position, self.old_enemy_address_to_new[level.enemy_offset] - BASE_OFFSET)

            if was_duplicate:
                continue

            last_enemy_end += level.enemy_data_length + ENEMY_DATA_DELIMITER_COUNT

    def _update_enemy_data_length_in_levels(self, sorted_levels):
        save_enemy_address, save_enemy_data = self.enemies_to_save

        for level in filter(lambda level_: level_.enemy_offset == save_enemy_address, sorted_levels):
            level.enemy_data_length = (
                len(save_enemy_data) - ENEMY_DATA_DELIMITER_COUNT
            )  # do not account for delimiters here

    def _sort_levels_by_enemy_address(self):
        return sorted(
            filter(lambda lvl: lvl.enemy_offset >= _ENEMY_BANK_START, self.levels),
            key=attrgetter("enemy_offset"),
        )
