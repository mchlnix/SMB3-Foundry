import json
from collections import defaultdict
from operator import attrgetter

from foundry.game.level import EnemyItemData, ObjectData
from smb3parse import PAGE_A000_ByTileset
from smb3parse.constants import BASE_OFFSET, ENEMY_DATA_BANK_INDEX, PAGE_A000_OFFSET
from smb3parse.util.parser import FoundLevel
from smb3parse.util.rom import PRG_BANK_SIZE, Rom


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

        free_space_start = last_level.level_offset + last_level.object_data_length + 1

        free_space_left = PRG_BANK_SIZE - (free_space_start % PRG_BANK_SIZE)

        return free_space_left

    def free_space_for_enemies(self):
        level_with_last_enemy_data = max(self.found_level_information, key=attrgetter("enemy_offset"))

        end_of_enemy_data = level_with_last_enemy_data.enemy_offset + level_with_last_enemy_data.enemy_data_length + 1

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


class LevelOrganizer:
    def __init__(
        self,
        rom: "Rom",
        levels: list[FoundLevel],
        level_to_save: ObjectData = (-1, bytearray()),
        enemies_to_save: EnemyItemData = (-1, bytearray()),
    ):
        self.rom = rom

        self.levels = levels

        self.level_to_save = level_to_save
        self.enemies_to_save = enemies_to_save

    def rearrange_levels(self):
        # 0.1 Sort Levels by bank
        prg_banks_by_object_set = self.rom.read(PAGE_A000_ByTileset, 16)

        levels_by_bank: dict[int, list[MovableLevel]] = defaultdict(list)

        for level in self.levels:
            levels_by_bank[prg_banks_by_object_set[level.object_set_number]].append(
                MovableLevel.from_found_level(level)
            )

        # 0.2 If a level is supposed to be saved, put the data of it into the movable level
        save_level_address, save_level_data = self.level_to_save

        if save_level_address != -1:
            level_found = False

            for levels in levels_by_bank.values():
                for level in levels:
                    if level.level_offset == save_level_address:
                        print("Found level to save")
                        level.level_data = save_level_data
                        level.object_data_length = len(save_level_data) - 1  # ignore delimiter here

                        level_found = True
                        break

                if level_found:
                    break

            else:
                raise LookupError(f"Could not find level, that was supposed to be saved. {save_level_address:x}")

        # 1. Sort levels by their level address
        for levels in levels_by_bank.values():
            levels.sort(key=attrgetter("level_offset"))

        # 2. Generate new level addresses based on the old ones and the level sizes
        old_level_address_to_new: dict[int, int] = dict()

        for levels in levels_by_bank.values():
            # 2.1. Take the first one as the bank start
            # FIXME: Figure out bank start on initial parsing and save that in additional data
            first_level = levels[0]

            new_level_start = first_level.level_offset

            # 2.2 Put them into a dictionary from old address to new address
            for level in levels:
                old_level_address_to_new[level.level_offset] = new_level_start
                new_level_start += level.object_data_length + 1  # one extra byte for the FF delimiter at the end

        # 3. Go through all levels and update their level position pointers, with the new addresses
        for bank, levels in levels_by_bank.items():
            object_set_offset = BASE_OFFSET + bank * PRG_BANK_SIZE - PAGE_A000_OFFSET

            # 3.1. Write new addresses in old positions, before actually moving the levels to the new position
            for level in levels:
                for position in level.level_offset_positions:
                    self.rom.write_little_endian(
                        position, old_level_address_to_new[level.level_offset] - object_set_offset
                    )

                level.level_base.level_offset_positions = [
                    old_level_address_to_new.get(position, position) for position in level.level_offset_positions
                ]

                for position in level.enemy_offset_positions:
                    if position - 2 in old_level_address_to_new:
                        print("BRUH", hex(position))

                level.level_base.enemy_offset_positions = [
                    old_level_address_to_new.get(position - 2, position - 2) + 2
                    for position in level.enemy_offset_positions
                ]

        # 4. Write level data to new position in bank
        for levels in levels_by_bank.values():
            # 4.1 Get level data from old position
            for level in levels:
                if not level.level_data:
                    level.level_data = self.rom.read(level.level_offset, level.object_data_length + 1)

            # 4.2 Save level data to new position
            for level in levels:
                new_level_offset = old_level_address_to_new[level.level_offset]

                print(hex(level.level_offset), "->", hex(new_level_offset))

                level.update_level_offset(new_level_offset)

                self.rom.write(new_level_offset, level.level_data)

    def rearrange_enemies(self):
        enemy_bank_start = PRG_BANK_SIZE * ENEMY_DATA_BANK_INDEX

        # 1. Sort levels based on their enemy offset (filter out enemy offsets, that aren't real/mean something else)
        levels = sorted(
            filter(lambda lvl: lvl.enemy_offset >= enemy_bank_start, self.levels),
            key=attrgetter("enemy_offset"),
        )

        print(f"---------------------------- {len(levels)}")

        # 0.2 If a level is supposed to be saved, put the data of it into the movable level
        save_enemy_address, save_enemy_data = self.enemies_to_save

        for level in levels:
            if level.enemy_offset == save_enemy_address:
                level.enemy_data_length = len(save_enemy_data) - 2  # do not account for delimiters here

        # 2. Set the start of the enemy data bank
        last_enemy_end = enemy_bank_start + BASE_OFFSET

        # 3. Go through the rest of the levels and adjust the enemy offsets to leave no empty space
        old_enemy_address_to_new: dict[int, int] = {}

        saved = 0

        # 4 Update enemy pointers with the new offset
        for level in levels:
            # some levels share enemies, so we don't count them again, otherwise we copy them into memory multiple times
            duplicate = level.enemy_offset in old_enemy_address_to_new

            if not duplicate:
                old_enemy_address_to_new[level.enemy_offset] = last_enemy_end
                print(
                    hex(level.level_offset),
                    hex(level.enemy_offset),
                    "->",
                    hex(old_enemy_address_to_new[level.enemy_offset]),
                    level.enemy_data_length,
                    "saved:",
                    f"{level.enemy_offset - last_enemy_end - saved}",
                )
            else:
                print(
                    hex(level.level_offset),
                    hex(level.enemy_offset),
                    "->",
                    hex(old_enemy_address_to_new[level.enemy_offset]),
                    level.enemy_data_length,
                )

            for position in level.enemy_offset_positions:
                print(
                    "enemy offset position",
                    hex(level.level_offset),
                    hex(position),
                    "writes",
                    hex(old_enemy_address_to_new[level.enemy_offset] - BASE_OFFSET),
                )
                self.rom.write_little_endian(position, old_enemy_address_to_new[level.enemy_offset] - BASE_OFFSET)

            if duplicate:
                continue

            saved = level.enemy_offset - last_enemy_end

            last_enemy_end += level.enemy_data_length + 2

        # 4. Finally, write the enemy data to their new positions
        # 4.1 Get enemy data from old position
        old_enemy_data_sets = {
            level.enemy_offset: self.rom.read(level.enemy_offset, level.enemy_data_length + 2) for level in levels
        }
        old_enemy_data_sets[save_enemy_address] = save_enemy_data

        already_copied = []

        for level in levels:
            # 4.2 Save enemy data to new position
            old_enemy_data = old_enemy_data_sets[level.enemy_offset]
            level.enemy_offset = old_enemy_address_to_new[level.enemy_offset]

            if level.enemy_offset not in already_copied:
                print(f"Writing {len(old_enemy_data)} to {level.enemy_offset:x}")
                self.rom.write(level.enemy_offset, old_enemy_data)
                already_copied.append(level.enemy_offset)

            else:
                print(f"Would've written to {level.enemy_offset:x} twice.")

        print(sum(level.enemy_data_length + 2 for level in levels))
