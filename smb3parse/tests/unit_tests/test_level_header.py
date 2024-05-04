from itertools import product
from pathlib import Path

import pytest
from hypothesis import given, strategies

from smb3parse.levels import (
    DEFAULT_HORIZONTAL_HEIGHT,
    DEFAULT_VERTICAL_WIDTH,
    HEADER_LENGTH,
    is_valid_level_length,
)
from smb3parse.levels.level_header import (
    MARIO_X_POSITIONS,
    MARIO_Y_POSITIONS,
    LevelHeader,
)
from smb3parse.objects.object_set import (
    MAX_OBJECT_SET,
    MIN_OBJECT_SET,
    PIPE_OBJECT_SET,
    PLAINS_OBJECT_SET,
    is_valid_object_set_number,
)
from smb3parse.tests.conftest import test_rom_path
from smb3parse.util.rom import Rom

rom = Rom.from_file(Path(test_rom_path))


@given(
    header_bytes=strategies.binary(min_size=9, max_size=9),
    object_set_number=strategies.integers(min_value=MIN_OBJECT_SET, max_value=MAX_OBJECT_SET),
)
def test_construction(header_bytes, object_set_number):
    level_header = LevelHeader(rom, header_bytes, object_set_number)

    if level_header.is_vertical:
        assert level_header.width == DEFAULT_VERTICAL_WIDTH
        assert is_valid_level_length(level_header.height)
    else:
        assert is_valid_level_length(level_header.width)
        assert level_header.height == DEFAULT_HORIZONTAL_HEIGHT

    assert level_header.music_index in range(16)
    assert level_header.time_index in range(4)
    assert level_header.scroll_type_index in range(4)

    assert level_header.start_x_index in range(4)
    assert level_header.start_y_index in range(8)
    assert level_header.start_action in range(8)

    assert level_header.object_palette_index in range(8)
    assert level_header.enemy_palette_index in range(4)
    assert level_header.graphic_set_index in range(32)

    assert is_valid_object_set_number(level_header.jump_object_set_number)


def test_value_error():
    with pytest.raises(ValueError, match="A level header is made up of"):
        LevelHeader(rom, bytearray(HEADER_LENGTH + 1), MIN_OBJECT_SET)

    with pytest.raises(ValueError, match="Object set number"):
        LevelHeader(rom, bytearray(HEADER_LENGTH), MAX_OBJECT_SET + 1)


def test_level_1_1():
    object_set_number = 1
    level_header_bytes = bytearray([0x93, 0xBC, 0x06, 0xC0, 0xEA, 0x80, 0x81, 0x01, 0x00])

    level_header = LevelHeader(rom, level_header_bytes, object_set_number)

    assert level_header.width == 0xB0  # blocks
    assert level_header.height == DEFAULT_HORIZONTAL_HEIGHT  # blocks

    assert level_header.music_index == 0
    assert level_header.time_index == 0
    assert level_header.scroll_type_index == 0

    assert not level_header.pipe_ends_level
    assert not level_header.is_vertical

    assert level_header.start_x_index == 0
    assert level_header.start_y_index == 7
    assert level_header.start_action == 0

    assert level_header.object_palette_index == 0
    assert level_header.enemy_palette_index == 0
    assert level_header.graphic_set_index == 1

    assert level_header.jump_enemy_address == 0xC016
    assert level_header.jump_level_address == 0x1FCA3


def test_level_1_1_bonus():
    object_set_number = 1
    level_header_bytes = bytearray([0x82, 0xBB, 0x27, 0xC5, 0x81, 0x85, 0xC1, 0x01, 0x01])

    level_header = LevelHeader(rom, level_header_bytes, object_set_number)

    assert level_header.width == 0x20  # blocks
    assert level_header.height == DEFAULT_HORIZONTAL_HEIGHT  # blocks

    assert level_header.music_index == 1
    assert level_header.time_index == 0
    assert level_header.scroll_type_index == 2

    assert not level_header.pipe_ends_level
    assert not level_header.is_vertical

    assert level_header.start_x_index == 0
    assert level_header.start_y_index == 4
    assert level_header.start_action == 0

    assert level_header.object_palette_index == 5
    assert level_header.enemy_palette_index == 0
    assert level_header.graphic_set_index == 1

    assert level_header.jump_enemy_address == 0xC537
    assert level_header.jump_level_address == 0x1FB92


def test_level_7_1():
    object_set_number = PIPE_OBJECT_SET
    level_header_bytes = bytearray([0x61, 0xAA, 0x4D, 0xC2, 0x07, 0x80, 0xB1, 0x08, 0x01])

    level_header = LevelHeader(rom, level_header_bytes, object_set_number)

    assert level_header.width == DEFAULT_VERTICAL_WIDTH  # blocks
    assert level_header.height == 0x80  # blocks

    assert level_header.music_index == 1
    assert level_header.time_index == 0
    assert level_header.scroll_type_index == 1

    assert not level_header.pipe_ends_level
    assert level_header.is_vertical

    assert level_header.start_x_index == 0
    assert level_header.start_y_index == 0
    assert level_header.start_action == 0

    assert level_header.object_palette_index == 0
    assert level_header.enemy_palette_index == 0
    assert level_header.graphic_set_index == 8

    assert level_header.jump_enemy_address == 0xC25D
    assert level_header.jump_level_address == 0x1EA71


def test_gen_mario_start_positions():
    level_header_bytes = bytearray([0x82, 0xBB, 0x27, 0xC5, 0x81, 0x85, 0xC1, 0x01, 0x01])
    horizontal_level_header = LevelHeader(rom, level_header_bytes, PLAINS_OBJECT_SET)

    level_header_bytes = bytearray([0x61, 0xAA, 0x4D, 0xC2, 0x07, 0x80, 0xB1, 0x08, 0x01])
    vertical_level_header = LevelHeader(rom, level_header_bytes, PIPE_OBJECT_SET)

    for level_header in (horizontal_level_header, vertical_level_header):
        for start_pos in level_header.gen_mario_start_positions():
            assert level_header.start_indexes_from_position(*start_pos)


def test_mario_start_indexes():
    level_header_bytes = bytearray([0x82, 0xBB, 0x27, 0xC5, 0x81, 0x85, 0xC1, 0x01, 0x01])
    horizontal_level_header = LevelHeader(rom, level_header_bytes, PLAINS_OBJECT_SET)

    level_header_bytes = bytearray([0x61, 0xAA, 0x4D, 0xC2, 0x07, 0x80, 0xB1, 0x08, 0x01])
    vertical_level_header = LevelHeader(rom, level_header_bytes, PIPE_OBJECT_SET)

    for level_header in (horizontal_level_header, vertical_level_header):
        for start_x, start_y in product(range(len(MARIO_X_POSITIONS)), range(len(MARIO_Y_POSITIONS))):
            position = level_header.position_from_start_index(start_x, start_y)
            assert (start_x, start_y) == level_header.start_indexes_from_position(*position)
