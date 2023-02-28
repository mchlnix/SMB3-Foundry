from itertools import pairwise
from random import randbytes

import pytest

from foundry.game.additional_data import LevelOrganizer
from foundry.game.level import EnemyItemAddress, LevelAddress
from smb3parse import PAGE_A000_ByTileset
from smb3parse.constants import BASE_OFFSET, ENEMY_DATA_BANK_INDEX, PLAINS_LEVEL_DATA_BANK_INDEX, VANILLA_PRG_BANK_COUNT
from smb3parse.objects.object_set import PLAINS_OBJECT_SET
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
            self.level_bytes = [randbytes(level_size) + bytes([0xFF]) for level_size in self.level_sizes]

            self.enemy_sizes = [24, 36, 48]
            self.enemy_bytes = [
                bytes([0x00]) + randbytes(enemy_size) + bytes([0xFF]) for enemy_size in self.enemy_sizes
            ]

            self.starting_level_offsets = [first_plains_level + offset for offset in [0, 188, 345]]
            self.expected_level_offsets = [
                first_plains_level + offset for offset in [0, self.level_sizes[0] + 1, sum(self.level_sizes[:2]) + 2]
            ]
            self.starting_enemy_offsets = [first_enemy_data + offset for offset in [0, 188, 345]]
            self.expected_enemy_offsets = [
                enemy_bank_start + offset for offset in [0, self.enemy_sizes[0] + 2, sum(self.enemy_sizes[:2]) + 4]
            ]

            for level_offset, level_data in zip(self.starting_level_offsets, self.level_bytes):
                super().write(level_offset, level_data)

            for enemy_offset, enemy_data in zip(self.starting_enemy_offsets, self.enemy_bytes):
                super().write(enemy_offset, enemy_data)

        def initial_levels(self):
            levels = []

            for level_offset, level_size, enemy_offset, enemy_size in zip(
                self.starting_level_offsets, self.level_sizes, self.starting_enemy_offsets, self.enemy_sizes
            ):
                level = _mk_level(level_offset, enemy_offset)
                level.object_data_length = level_size
                level.enemy_data_length = enemy_size

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


def test_rearrange_levels_with_larger_data(mock_rom):
    # GIVEN a LevelOrganizer with a MockROM
    larger_level = mock_rom.initial_levels()[1]
    new_size = larger_level.object_data_length + 0x50

    mock_rom.expected_level_offsets[2] = mock_rom.expected_level_offsets[1] + new_size + 1
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
        assert level_2.enemy_offset == level_1.enemy_offset + level_1.enemy_data_length + 2


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

    mock_rom.expected_enemy_offsets[2] = mock_rom.expected_enemy_offsets[1] + new_size + 2
    new_bytes = bytearray(randbytes(new_size) + bytes([0xFF]))

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
