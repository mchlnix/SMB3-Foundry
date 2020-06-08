import os
from itertools import product
from pathlib import Path

import pytest

from foundry import root_dir
from foundry.conftest import compare_images
from foundry.game.File import ROM
from foundry.game.gfx.objects.LevelObject import get_minimal_icon_object
from foundry.game.gfx.objects.LevelObjectFactory import LevelObjectFactory
from foundry.gui.ObjectViewer import ObjectDrawArea
from smb3parse.objects import MAX_DOMAIN, MAX_ID_VALUE
from smb3parse.objects.object_set import (
    DUNGEON_GRAPHICS_SET,
    DUNGEON_OBJECT_SET,
    HILLY_GRAPHICS_SET,
    HILLY_OBJECT_SET,
    MAX_OBJECT_SET,
    MUSHROOM_OBJECT_SET,
    SPADE_BONUS_OBJECT_SET,
    UNDERGROUND_GRAPHICS_SET,
    UNDERGROUND_OBJECT_SET,
    WORLD_MAP_OBJECT_SET,
)

reference_image_dir = Path(__file__).parent.joinpath("test_refs")
os.makedirs(reference_image_dir, exist_ok=True)


def _test_object_against_reference(level_object, qtbot, minimal=False):
    object_set_number = level_object.object_set.number
    view = ObjectDrawArea(None, object_set_number, object_set_number)

    qtbot.addWidget(view)

    view.update_object(level_object)

    view.setGeometry(0, 0, *level_object.display_size().toTuple())

    image_name = f"object_set_{object_set_number}_domain_{level_object.domain}_index_{hex(level_object.obj_index)}.png"

    if minimal:
        image_name = "minimal_" + image_name

    ref_image_path = str(reference_image_dir.joinpath(image_name))

    compare_images(image_name, ref_image_path, view.grab())


@pytest.mark.parametrize(
    "domain, object_index",
    [
        (0, 0x30),  # Weird 45-Degree Hill
        (0, 0x3C),
        (3, 0x30),  # Weird 30-Degree Hill
        (3, 0x3A),
        (3, 0x70),  # 30 Degree Hill - Up/Left
        (3, 0x7A),
        (3, 0xB0),  # 30 Degree Underwater Hill - Up/Left
        (3, 0xBA),
    ],
)
def test_object_rendering_4_2(domain, object_index, qtbot):
    object_factory = LevelObjectFactory(HILLY_OBJECT_SET, HILLY_GRAPHICS_SET, 0, [], False)

    level_object = object_factory.from_properties(domain, object_index, 0, 0, None, 0)

    _test_object_against_reference(level_object, qtbot)


@pytest.mark.parametrize("object_index", [0x80, 0x8F])  # 45 Degree Hill - Up/Right
def test_object_rendering_8_1(object_index, qtbot):
    object_factory = LevelObjectFactory(UNDERGROUND_OBJECT_SET, UNDERGROUND_GRAPHICS_SET, 0, [], False)

    object_domain = 0x00
    level_object = object_factory.from_properties(object_domain, object_index, 0, 0, None, 0)

    _test_object_against_reference(level_object, qtbot)


@pytest.mark.parametrize(
    "object_index, domain, object_set, graphic_set",
    [
        (0x20, 0x00, UNDERGROUND_OBJECT_SET, UNDERGROUND_GRAPHICS_SET),  # 45 Degree Underground Hill - Down/Left
        (0x2F, 0x00, UNDERGROUND_OBJECT_SET, UNDERGROUND_GRAPHICS_SET),
        (0x60, 0x03, HILLY_OBJECT_SET, HILLY_GRAPHICS_SET),  # 30 Degree Hill - Down/Left
        (0x6F, 0x03, HILLY_OBJECT_SET, HILLY_GRAPHICS_SET),
        (0xA0, 0x03, UNDERGROUND_OBJECT_SET, UNDERGROUND_GRAPHICS_SET),  # 30 Degree Underwater Hill - Down/Left
        (0xAF, 0x03, UNDERGROUND_OBJECT_SET, UNDERGROUND_GRAPHICS_SET),
    ],
)
def test_object_rendering_2_1(object_index, domain, object_set, graphic_set, qtbot):
    object_factory = LevelObjectFactory(object_set, graphic_set, 0, [], False)

    level_object = object_factory.from_properties(domain, object_index, 0, 0, None, 0)

    _test_object_against_reference(level_object, qtbot)


@pytest.mark.parametrize(
    "object_index, domain, object_set, graphic_set",
    [
        (0x50, 0x04, UNDERGROUND_OBJECT_SET, UNDERGROUND_GRAPHICS_SET),  # Hilly Wall
        (0x5F, 0x04, UNDERGROUND_OBJECT_SET, UNDERGROUND_GRAPHICS_SET),
    ],
)
def test_object_rendering_0_0(object_index, domain, object_set, graphic_set, qtbot):
    object_factory = LevelObjectFactory(object_set, graphic_set, 0, [], False)

    level_object = object_factory.from_properties(domain, object_index, 0, 0, 8, 0)

    _test_object_against_reference(level_object, qtbot)


@pytest.mark.parametrize(
    "object_index, domain, object_set, graphic_set",
    [
        (0xF0, 0x0, DUNGEON_OBJECT_SET, DUNGEON_GRAPHICS_SET),  # Vertically oriented X-blocks
        (0xF7, 0x0, DUNGEON_OBJECT_SET, DUNGEON_GRAPHICS_SET),
    ],
)
def test_object_rendering_1_0_1(object_index, domain, object_set, graphic_set, qtbot):
    object_factory = LevelObjectFactory(object_set, graphic_set, 0, [], False)

    level_object = object_factory.from_properties(domain, object_index, 0, 0, 8, 0)

    _test_object_against_reference(level_object, qtbot)


def test_no_change_to_bytes():
    object_factory = LevelObjectFactory(1, 1, 0, [], False)

    cloud_bytes = bytearray([0x00, 0x00, 0xE5])

    cloud_object = object_factory.from_data(cloud_bytes, 0)

    assert cloud_object.to_bytes() == cloud_bytes


@pytest.mark.parametrize(
    "attribute, increase", zip(["domain", "obj_index", "length", "x_position", "y_position"], [1, 0x10, 1, 1, 1])
)
def test_change_attribute_to_bytes(attribute, increase):
    object_factory = LevelObjectFactory(1, 1, 0, [], False)

    cloud_object = object_factory.from_properties(0x00, 0xE0, 0, 0, None, 0)

    initial_bytes = cloud_object.to_bytes()

    setattr(cloud_object, attribute, getattr(cloud_object, attribute) + increase)

    assert cloud_object.to_bytes() != initial_bytes


def gen_object_factories():
    ROM(root_dir.joinpath("SMB3.nes"))

    for object_set in range(MAX_OBJECT_SET + 1):
        if object_set in [WORLD_MAP_OBJECT_SET, MUSHROOM_OBJECT_SET, SPADE_BONUS_OBJECT_SET]:
            continue

        yield LevelObjectFactory(object_set, object_set, 0, [], False)


def gen_object_ids():
    for id_ in range(0x10):
        yield id_

    for id_ in range(0x10, MAX_ID_VALUE, 0x10):
        yield id_
        yield id_ + 6


@pytest.mark.parametrize(
    "factory, domain, obj_id", list(product(gen_object_factories(), range(0, MAX_DOMAIN), gen_object_ids()))
)
def test_all_objects(factory, domain, obj_id, qtbot):
    level_object = factory.from_properties(domain, obj_id, 0, 0, 8, 0)

    _test_object_against_reference(level_object, qtbot)


@pytest.mark.parametrize(
    "factory, domain, obj_id", list(product(gen_object_factories(), range(0, MAX_DOMAIN), gen_object_ids()))
)
def test_all_minimal_objects(factory, domain, obj_id, qtbot):
    level_object = factory.from_properties(domain, obj_id, 0, 0, 0, 0)

    _test_object_against_reference(get_minimal_icon_object(level_object), qtbot, minimal=True)
