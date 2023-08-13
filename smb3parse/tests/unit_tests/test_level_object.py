import pytest

from smb3parse.objects import MAX_Y_VALUE
from smb3parse.objects.level_object import LevelObject


@pytest.fixture
def all_zero_3_byte_object_data():
    return bytearray([0x00, 0x00, 0x00])


@pytest.fixture
def all_zero_4_byte_object_data():
    return bytearray([0x00, 0x00, 0x00, 0x00])


def test_value_error_y(all_zero_3_byte_object_data, all_zero_4_byte_object_data):
    # GIVEN data for 3 and 4 byte objects, where everything is set to 0

    # WHEN illegal values are encoded in the data
    bad_y_3_byte = all_zero_3_byte_object_data.copy()
    bad_y_3_byte[0] |= MAX_Y_VALUE + 1

    bad_y_4_byte = all_zero_4_byte_object_data.copy()
    bad_y_4_byte[0] |= MAX_Y_VALUE + 1

    # THEN a ValueError is raised
    for bad_data in [bad_y_3_byte, bad_y_4_byte]:
        with pytest.raises(ValueError, match="Data designating y value cannot be"):
            LevelObject(bad_data)


def test_value_error():
    with pytest.raises(ValueError, match="Length of the given data"):
        LevelObject(bytearray(5))
