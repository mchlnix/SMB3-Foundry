from itertools import pairwise
from random import randbytes, shuffle

import pytest

from foundry.game.additional_data import ENEMY_DATA_DELIMITER_COUNT, LEVEL_DATA_DELIMITER_COUNT, LevelOrganizer
from foundry.game.level import EMPTY_OBJECT_DATA, EnemyItemAddress, LevelAddress
from smb3parse import PAGE_A000_ByTileset
from smb3parse.constants import (
    BASE_OFFSET,
    ENEMY_DATA_BANK_INDEX,
    OFFSET_SIZE,
    PLAINS_LEVEL_DATA_BANK_INDEX,
    VANILLA_PRG_BANK_COUNT,
)
from smb3parse.objects.object_set import DESERT_OBJECT_SET, PLAINS_OBJECT_SET
from smb3parse.util.parser import FoundLevel
from smb3parse.util.rom import PRG_BANK_SIZE, Rom

enemy_bank_start = BASE_OFFSET + PRG_BANK_SIZE * ENEMY_DATA_BANK_INDEX
first_enemy_data = enemy_bank_start + 5

plains_bank_start = BASE_OFFSET + PRG_BANK_SIZE * PLAINS_LEVEL_DATA_BANK_INDEX
first_plains_level = plains_bank_start + PRG_BANK_SIZE // 2

enemy_size = 0x50
level_size = 0x50

enemy_offset_diff = 0x100
level_offset_diff = 0x100

level_count = 10


@pytest.fixture
def mock_rom(rom):
    class MockROM(Rom):
        def __init__(self):
            super().__init__(bytearray(VANILLA_PRG_BANK_COUNT * PRG_BANK_SIZE))

            super().write(PAGE_A000_ByTileset, rom.read(PAGE_A000_ByTileset, 16))

            self.level_sizes = [24, 36, 48]
            self.level_bytes = [randbytes(level_size_) + bytes([0xFF]) for level_size_ in self.level_sizes]

            self.enemy_sizes = [24, 36, 48]
            self.enemy_bytes = [
                bytes([0x00]) + randbytes(enemy_size_) + bytes([0xFF]) for enemy_size_ in self.enemy_sizes
            ]

            self.starting_level_offsets = [first_plains_level + offset for offset in [0, 188, 345]]
            self.expected_level_offsets = [
                first_plains_level + offset
                for offset in [
                    0,
                    self.level_sizes[0] + LEVEL_DATA_DELIMITER_COUNT,
                    sum(self.level_sizes[:2]) + 2 * LEVEL_DATA_DELIMITER_COUNT,
                ]
            ]
            self.starting_enemy_offsets = [first_enemy_data + offset for offset in [0, 188, 345]]
            self.expected_enemy_offsets = [
                enemy_bank_start + offset
                for offset in [
                    0,
                    self.enemy_sizes[0] + ENEMY_DATA_DELIMITER_COUNT,
                    sum(self.enemy_sizes[:2]) + 2 * ENEMY_DATA_DELIMITER_COUNT,
                ]
            ]

            for level_offset, level_data in zip(self.starting_level_offsets, self.level_bytes):
                super().write(level_offset, level_data)

            for enemy_offset, enemy_data in zip(self.starting_enemy_offsets, self.enemy_bytes):
                super().write(enemy_offset, enemy_data)

        def initial_levels(self):
            levels = []

            for level_offset, level_size_, enemy_offset, enemy_size_ in zip(
                self.starting_level_offsets, self.level_sizes, self.starting_enemy_offsets, self.enemy_sizes
            ):
                level = _mk_level(level_offset, enemy_offset)
                level.object_data_length = level_size_
                level.enemy_data_length = enemy_size_

                levels.append(level)

            return levels

    return MockROM()


def _mk_level(level_offset: LevelAddress, enemy_offset: EnemyItemAddress):
    level = FoundLevel(
        level_offset_positions=[],
        enemy_offset_positions=[],
        world_number=1,
        level_offset=level_offset,
        enemy_offset=enemy_offset,
        object_set_number=PLAINS_OBJECT_SET,
        object_data_length=level_size,
        enemy_data_length=enemy_size,
        found_in_world=False,
        found_as_jump=False,
        is_generic=False,
    )

    return level


@pytest.fixture
def level_organizer(rom):
    level_list = [
        _mk_level(first_plains_level + level_offset, first_enemy_data + enemy_offset)
        for level_offset, enemy_offset in zip(
            range(0, level_count * level_offset_diff, level_offset_diff),
            range(0, level_count * enemy_offset_diff, enemy_offset_diff),
        )
    ]

    return LevelOrganizer(rom, level_list)


@pytest.fixture
def level_organizer_with_duplicates(level_organizer):
    # add level with the same enemies as another one in the list already
    level_organizer.levels.append(
        FoundLevel(
            [], [], 1, 0, first_enemy_data + level_count // 2 * enemy_offset_diff, 1, 0, enemy_size, False, False, False
        )
    )

    return level_organizer


# LEVELS #


def test_rearrange_levels(mock_rom):
    # GIVEN a LevelOrganizer with a MockROM
    level_organizer = LevelOrganizer(mock_rom, mock_rom.initial_levels())

    # WHEN the level data is rearranged
    level_organizer.rearrange_levels()
    new_level_offsets = [level.level_offset for level in level_organizer.levels]

    # THEN the level data should be as expected
    assert new_level_offsets != mock_rom.starting_level_offsets, "Nothing happened"

    for level, expected_level_offset in zip(level_organizer.levels, mock_rom.expected_level_offsets):
        assert hex(level.level_offset) == hex(expected_level_offset), list(map(hex, mock_rom.expected_level_offsets))

    for expected_level_offset, level_bytes in zip(mock_rom.expected_level_offsets, mock_rom.level_bytes):
        assert mock_rom.read(expected_level_offset, len(level_bytes)) == level_bytes


def test_rearrange_levels_consistency(level_organizer):
    # GIVEN a LevelOrganizer
    pass

    # WHEN we let it rearrange the level data more than once in a row
    level_organizer.rearrange_levels()
    first_result = [level.level_offset for level in level_organizer.levels]

    level_organizer.rearrange_levels()
    second_result = [level.level_offset for level in level_organizer.levels]

    # THEN the result will not change a second time
    assert first_result == second_result
    assert all(
        old_address == new_address for old_address, new_address in level_organizer.old_level_address_to_new.items()
    )


def test_rearrange_levels_with_larger_data(mock_rom):
    # GIVEN a LevelOrganizer with a MockROM
    larger_level = mock_rom.initial_levels()[1]
    new_size = larger_level.object_data_length + 0x50

    mock_rom.expected_level_offsets[2] = mock_rom.expected_level_offsets[1] + new_size + LEVEL_DATA_DELIMITER_COUNT
    new_bytes = bytearray(randbytes(new_size) + bytes([0xFF]))

    level_organizer = LevelOrganizer(
        mock_rom, mock_rom.initial_levels(), level_to_save=(larger_level.level_offset, new_bytes)
    )
    level_organizer.rearrange_levels()

    mock_rom.level_bytes[1] = new_bytes

    # WHEN the level data is rearranged while saving one of the levels with larger data
    new_level_offsets = [level.level_offset for level in level_organizer.levels]

    # THEN the level data should be as expected
    assert new_level_offsets != mock_rom.starting_level_offsets, "Nothing happened"

    for level, expected_level_offset in zip(level_organizer.levels, mock_rom.expected_level_offsets):
        assert hex(level.level_offset) == hex(expected_level_offset), list(map(hex, mock_rom.expected_level_offsets))

    for expected_level_offset, level_bytes in zip(mock_rom.expected_level_offsets, mock_rom.level_bytes):
        assert mock_rom.read(expected_level_offset, len(level_bytes)) == level_bytes


def test_separate_levels_by_banks(level_organizer):
    # GIVEN a level organizer and levels of different object sets
    additional_level = _mk_level(0, 0)
    additional_level.object_set_number = DESERT_OBJECT_SET

    # All levels in the level organizer object are of type plains, so add another level with a different object set
    level_organizer.levels.append(additional_level)

    # WHEN the levels are separated by the respective Banks they are located in
    level_organizer._separate_levels_by_banks()

    # THEN the 10 plain levels land in bank 15 and the added desert level in bank 20
    bank_for_plains = 15
    assert len(level_organizer.levels_by_bank[bank_for_plains]) == len(level_organizer.levels[:10])

    bank_for_desert = 20
    assert len(level_organizer.levels_by_bank[bank_for_desert]) == len(level_organizer.levels[10:])

    assert level_organizer.levels_by_bank.keys() == {15: [], 20: []}.keys()


@pytest.mark.parametrize(
    "level_to_save", [EMPTY_OBJECT_DATA, (first_plains_level + 2 * level_offset_diff, bytearray(20))]
)
def test_inject_level_to_be_saved(level_organizer, level_to_save):
    level_organizer.level_to_save = level_to_save

    level_organizer._separate_levels_by_banks()

    found_level = level_organizer._inject_level_to_be_saved()

    if level_to_save is EMPTY_OBJECT_DATA:
        assert found_level is None
    else:
        assert found_level is not None
        assert found_level.level_base in level_organizer.levels


def test_sort_levels(level_organizer):
    level_organizer._separate_levels_by_banks()
    level_organizer._sort_levels_by_level_address()

    for bank, levels in level_organizer.levels_by_bank.items():
        for level_1, level_2 in pairwise(levels):
            assert level_1.level_offset < level_2.level_offset


def test_generate_new_level_addresses(level_organizer):
    starting_addresses = [level.level_offset for level in level_organizer.levels]

    level_organizer._separate_levels_by_banks()
    level_organizer._sort_levels_by_level_address()

    level_organizer._generate_new_level_addresses()

    assert all(initial_address in level_organizer.old_level_address_to_new for initial_address in starting_addresses)

    # First one stays the same
    assert level_organizer.old_level_address_to_new[starting_addresses[0]] == starting_addresses[0]

    for initial_address in starting_addresses[1:]:
        new_address = level_organizer.old_level_address_to_new[initial_address]

        assert new_address < initial_address


def test_generate_new_level_addresses_larger(level_organizer):
    level_organizer.rearrange_levels()

    level_to_make_bigger_index = len(level_organizer.levels) // 2
    level = level_organizer.levels[level_to_make_bigger_index]

    size_increase = 50
    level.object_data_length += size_increase

    level_organizer._separate_levels_by_banks()
    level_organizer._sort_levels_by_level_address()
    level_organizer._generate_new_level_addresses()

    for initial_address, new_address in list(level_organizer.old_level_address_to_new.items())[
        : level_to_make_bigger_index + 1
    ]:
        assert new_address == initial_address, (level_to_make_bigger_index, level_organizer.old_level_address_to_new)

    for initial_address, new_address in list(level_organizer.old_level_address_to_new.items())[
        level_to_make_bigger_index + 1 :
    ]:
        assert new_address == initial_address + size_increase


def test_update_level_and_enemy_address_pointers(level_organizer):
    level_organizer.rearrange_levels()

    level_to_make_bigger_index = len(level_organizer.levels) // 2
    level = level_organizer.levels[level_to_make_bigger_index]

    size_increase = 50
    level.object_data_length += size_increase

    # set level positions here locally, as to not interfere with other tests
    for level in level_organizer.levels:
        level.level_offset_positions = [level.level_offset]
        level.enemy_offset_positions = [level.level_offset + OFFSET_SIZE]

    level_organizer._separate_levels_by_banks()
    level_organizer._sort_levels_by_level_address()
    level_organizer._generate_new_level_addresses()

    old_level_positions = {level.level_offset: level.level_offset_positions for level in level_organizer.levels}
    old_enemy_positions = {level.level_offset: level.enemy_offset_positions for level in level_organizer.levels}

    level_organizer._update_level_and_enemy_pointers()

    for level in level_organizer.levels[: level_to_make_bigger_index + 1]:
        for new_position, old_position in zip(level.level_offset_positions, old_level_positions[level.level_offset]):
            assert new_position == old_position, (level_to_make_bigger_index, level_organizer.old_level_address_to_new)

        for new_position, old_position in zip(level.enemy_offset_positions, old_enemy_positions[level.level_offset]):
            assert new_position == old_position

    for level in level_organizer.levels[level_to_make_bigger_index + 1 :]:
        for new_position, old_position in zip(level.level_offset_positions, old_level_positions[level.level_offset]):
            assert new_position == old_position + size_increase

        for new_position, old_position in zip(level.enemy_offset_positions, old_enemy_positions[level.level_offset]):
            assert new_position == old_position + size_increase


# ENEMIES #


def test_rearrange_enemies(level_organizer):
    # GIVEN a LevelOrganizer
    before_rearrange = [level.enemy_offset for level in level_organizer.levels]

    # WHEN the enemy data is rearranged
    level_organizer.rearrange_enemies()
    new_enemy_offsets = [level.enemy_offset for level in level_organizer.levels]

    # THEN the enemy data should be contiguous
    assert before_rearrange != new_enemy_offsets, "Nothing happened"

    assert new_enemy_offsets[0] == enemy_bank_start, "First Enemy Data doesn't start at bank start"

    for level_1, level_2 in pairwise(level_organizer.levels):
        assert level_2.enemy_offset == level_1.enemy_offset + level_1.enemy_data_length + ENEMY_DATA_DELIMITER_COUNT


def test_rearrange_enemies_dont_duplicate_data(level_organizer_with_duplicates):
    # GIVEN a LevelOrganizer with levels referencing the same enemy data
    pass

    # WHEN the enemy data is rearranged
    level_organizer_with_duplicates.rearrange_enemies()
    new_enemy_offsets = [level.enemy_offset for level in level_organizer_with_duplicates.levels]

    # THEN the duplicate enemy data should not have been placed at separate locations
    assert len(set(new_enemy_offsets)) == len(new_enemy_offsets) - 1


def test_rearrange_enemies_consistency(level_organizer):
    # GIVEN a LevelOrganizer
    pass

    # WHEN we let it rearrange the enemy data more than once in a row
    level_organizer.rearrange_enemies()
    first_result = [level.enemy_offset for level in level_organizer.levels]

    level_organizer.rearrange_enemies()
    second_result = [level.enemy_offset for level in level_organizer.levels]

    # THEN the result will not change a second time
    assert first_result == second_result


def test_rearrange_enemies_with_larger_data(mock_rom):
    # GIVEN a LevelOrganizer with a MockROM
    larger_level = mock_rom.initial_levels()[1]
    new_size = larger_level.enemy_data_length + 0x50

    mock_rom.expected_enemy_offsets[2] = mock_rom.expected_enemy_offsets[1] + new_size + ENEMY_DATA_DELIMITER_COUNT
    new_bytes = bytearray(bytes([0x00]) + randbytes(new_size) + bytes([0xFF]))

    level_organizer = LevelOrganizer(
        mock_rom, mock_rom.initial_levels(), enemies_to_save=(larger_level.enemy_offset, new_bytes)
    )
    level_organizer.rearrange_enemies()

    mock_rom.enemy_bytes[1] = new_bytes

    # WHEN the level data is rearranged while saving one of the levels with larger data
    new_enemy_offsets = [level.enemy_offset for level in level_organizer.levels]

    # THEN the level data should be as expected
    assert new_enemy_offsets != mock_rom.starting_enemy_offsets, "Nothing happened"

    for level, expected_enemy_offset in zip(level_organizer.levels, mock_rom.expected_enemy_offsets):
        assert hex(level.enemy_offset) == hex(expected_enemy_offset), list(map(hex, mock_rom.expected_enemy_offsets))

    for expected_enemy_offset, enemy_bytes in zip(mock_rom.expected_enemy_offsets, mock_rom.enemy_bytes):
        assert mock_rom.read(expected_enemy_offset, len(enemy_bytes)) == enemy_bytes


def test_sort_levels_by_enemy_address(level_organizer):
    shuffle(level_organizer.levels)

    sorted_levels = level_organizer._sort_levels_by_enemy_address()

    assert sorted_levels != level_organizer.levels

    for level_1, level_2 in pairwise(sorted_levels):
        assert level_1.enemy_offset < level_2.enemy_offset


@pytest.mark.parametrize("size_change", [20, -20])
def test_update_enemy_data_length_in_levels(level_organizer, size_change):
    chosen_level = level_organizer.levels[3]
    enemy_address_of_a_level = chosen_level.enemy_offset
    original_enemy_size = chosen_level.enemy_data_length

    level_organizer.enemies_to_save = (
        enemy_address_of_a_level,
        bytearray(original_enemy_size + size_change + ENEMY_DATA_DELIMITER_COUNT),
    )

    level_organizer._update_enemy_data_length_in_levels(level_organizer._sort_levels_by_enemy_address())

    assert chosen_level.enemy_data_length == original_enemy_size + size_change


@pytest.mark.parametrize("size_change", [20, -20])
def test_generate_new_enemy_addresses(level_organizer, size_change):
    level_organizer.rearrange_enemies()

    old_enemy_offsets = sorted([level.enemy_offset for level in level_organizer.levels])

    index_of_chosen_level = 2
    chosen_level = level_organizer.levels[index_of_chosen_level]
    enemy_address_of_a_level = chosen_level.enemy_offset
    original_enemy_size = chosen_level.enemy_data_length

    level_organizer.enemies_to_save = (
        enemy_address_of_a_level,
        bytearray(original_enemy_size + size_change + ENEMY_DATA_DELIMITER_COUNT),
    )

    sorted_levels = level_organizer._sort_levels_by_enemy_address()
    level_organizer._update_enemy_data_length_in_levels(sorted_levels)
    level_organizer._generate_new_enemy_addresses(sorted_levels)

    for old_enemy_offset in old_enemy_offsets[: index_of_chosen_level + 1]:
        new_offset = level_organizer.old_enemy_address_to_new[old_enemy_offset]
        assert old_enemy_offset == new_offset

    for old_enemy_offset in old_enemy_offsets[index_of_chosen_level + 1 :]:
        new_offset = level_organizer.old_enemy_address_to_new[old_enemy_offset]
        assert old_enemy_offset == new_offset - size_change, (
            old_enemy_offsets,
            level_organizer.old_enemy_address_to_new,
        )


def test_collect_enemy_data_from_current_addresses(mock_rom):
    level_organizer = LevelOrganizer(mock_rom, mock_rom.initial_levels())

    sorted_levels = level_organizer._sort_levels_by_enemy_address()

    address_to_enemy_data = level_organizer._collect_enemy_data_from_current_addresses(sorted_levels)

    assert len(mock_rom.enemy_bytes) == len(address_to_enemy_data.values())
    assert all(enemy_offset in address_to_enemy_data for enemy_offset in mock_rom.starting_enemy_offsets)
    assert all(enemy_data in address_to_enemy_data.values() for enemy_data in mock_rom.enemy_bytes)
