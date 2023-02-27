from itertools import pairwise

import pytest

from foundry.game.additional_data import LevelOrganizer
from smb3parse.constants import BASE_OFFSET, ENEMY_DATA_BANK_INDEX
from smb3parse.util.parser import FoundLevel
from smb3parse.util.rom import PRG_BANK_SIZE

enemy_bank_start = BASE_OFFSET + PRG_BANK_SIZE * ENEMY_DATA_BANK_INDEX
first_enemy_data = enemy_bank_start + 5
enemy_size = 0x50
enemy_offset_diff = 0x100
level_count = 10


@pytest.fixture
def level_organizer(rom):
    level_list = [
        FoundLevel([], [], 1, 0, first_enemy_data + enemy_offset, 1, 0, enemy_size, False, False, False)
        for enemy_offset in range(0, level_count * enemy_offset_diff, enemy_offset_diff)
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
