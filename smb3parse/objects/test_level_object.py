import pytest
from hypothesis import given, strategies

from smb3parse.objects import (
    MIN_DOMAIN,
    MAX_DOMAIN,
    MIN_Y_VALUE,
    MAX_Y_VALUE,
    MIN_ID_VALUE,
    MAX_ID_VALUE,
    MIN_X_VALUE,
    MAX_X_VALUE,
)
from smb3parse.objects.level_object import LevelObject


def check_object_for_0s(level_object: LevelObject, attribute_name, expected_value):
    attributes_to_check = ["x", "y", "id", "domain"]

    for attribute in attributes_to_check:
        if attribute != attribute_name:
            assert getattr(level_object, attribute) == 0
        else:
            assert getattr(level_object, attribute_name) == expected_value

    if level_object.has_additional_length:
        if attribute_name == "additional_length":
            assert level_object.additional_length == expected_value
        else:
            assert level_object.additional_length == 0


def valid_y_value_in_byte(byte: int):
    return (byte & 0b0001_1111) <= MAX_Y_VALUE


@pytest.fixture
def all_zero_3_byte_object_data():
    return bytearray([0x00, 0x00, 0x00])


@pytest.fixture
def all_zero_4_byte_object_data():
    return bytearray([0x00, 0x00, 0x00, 0x00])


@pytest.mark.parametrize("expected_domain", list(range(MIN_DOMAIN, MAX_DOMAIN + 1)))
def test_parsing_domain(all_zero_3_byte_object_data, all_zero_4_byte_object_data, expected_domain):
    # GIVEN data for 3 and 4 byte objects, where everything is set to 0 and an expected domain value
    all_zero_3_byte_object_data[0] |= expected_domain << 5
    all_zero_4_byte_object_data[0] |= expected_domain << 5

    # WHEN LevelObjects are created with the modified data
    level_object_3_byte = LevelObject(all_zero_3_byte_object_data)
    level_object_4_byte = LevelObject(all_zero_4_byte_object_data)

    # THEN the resulting object should have the expected domain
    check_object_for_0s(level_object_3_byte, "domain", expected_domain)
    check_object_for_0s(level_object_4_byte, "domain", expected_domain)


@pytest.mark.parametrize("expected_y", list(range(MIN_Y_VALUE, MAX_Y_VALUE + 1)))
def test_parsing_y(all_zero_3_byte_object_data, all_zero_4_byte_object_data, expected_y):
    # GIVEN data for 3 and 4 byte objects, where everything is set to 0 and an expected y value
    all_zero_3_byte_object_data[0] &= 0b1110_0000
    all_zero_3_byte_object_data[0] |= expected_y

    all_zero_4_byte_object_data[0] &= 0b1110_0000
    all_zero_4_byte_object_data[0] |= expected_y

    # WHEN LevelObjects are created with the modified data
    level_object_3_byte = LevelObject(all_zero_3_byte_object_data)
    level_object_4_byte = LevelObject(all_zero_4_byte_object_data)

    # THEN the resulting object should have the expected y position
    check_object_for_0s(level_object_3_byte, "y", expected_y)
    check_object_for_0s(level_object_4_byte, "y", expected_y)


@pytest.mark.parametrize("expected_id", list(range(MIN_ID_VALUE, MAX_ID_VALUE + 1)))
def test_parsing_id(all_zero_3_byte_object_data, all_zero_4_byte_object_data, expected_id):
    # GIVEN data for 3 and 4 byte objects, where everything is set to 0 and an expected id value
    all_zero_3_byte_object_data[1] = expected_id
    all_zero_4_byte_object_data[1] = expected_id

    # WHEN LevelObjects are created with the modified data
    level_object_3_byte = LevelObject(all_zero_3_byte_object_data)
    level_object_4_byte = LevelObject(all_zero_4_byte_object_data)

    # THEN the resulting object should have the expected id value
    check_object_for_0s(level_object_3_byte, "id", expected_id)
    check_object_for_0s(level_object_4_byte, "id", expected_id)


@pytest.mark.parametrize("expected_x", list(range(MIN_X_VALUE, MAX_X_VALUE + 1)))
def test_parsing_x(all_zero_3_byte_object_data, all_zero_4_byte_object_data, expected_x):
    # GIVEN data for 3 and 4 byte objects, where everything is set to 0 and an expected x value
    all_zero_3_byte_object_data[2] = expected_x
    all_zero_4_byte_object_data[2] = expected_x

    # WHEN LevelObjects are created with the modified data
    level_object_3_byte = LevelObject(all_zero_3_byte_object_data)
    level_object_4_byte = LevelObject(all_zero_4_byte_object_data)

    # THEN the resulting object should have the expected x position
    check_object_for_0s(level_object_3_byte, "x", expected_x)
    check_object_for_0s(level_object_4_byte, "x", expected_x)


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


@given(data=strategies.binary(min_size=3, max_size=4).filter(lambda data: valid_y_value_in_byte(data[0])))
def test_object_construction(data):
    LevelObject(data)
