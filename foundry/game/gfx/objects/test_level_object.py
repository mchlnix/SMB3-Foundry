import os
from pathlib import Path

import pytest

from foundry.conftest import compare_images
from foundry.game.gfx.objects.LevelObjectFactory import LevelObjectFactory
from foundry.gui.ObjectViewer import ObjectDrawArea
from smb3parse.objects.object_set import (
    HILLY_GRAPHICS_SET,
    HILLY_OBJECT_SET,
    PLAINS_GRAPHICS_SET,
    PLAINS_OBJECT_SET,
    UNDERGROUND_GRAPHICS_SET,
    UNDERGROUND_OBJECT_SET,
)

reference_image_dir = Path(__file__).parent.joinpath("test_refs")
os.makedirs(reference_image_dir, exist_ok=True)


def _test_object_against_reference(level_object, qtbot):
    object_set_number = level_object.object_set.number
    view = ObjectDrawArea(None, object_set_number, object_set_number)

    qtbot.addWidget(view)

    view.update_object(level_object)

    view.setGeometry(0, 0, *level_object.display_size().toTuple())

    image_name = f"object_set_{object_set_number}_domain_{level_object.domain}_index_{hex(level_object.obj_index)}.png"
    ref_image_path = str(reference_image_dir.joinpath(image_name))

    compare_images(image_name, ref_image_path, view.grab())


@pytest.mark.parametrize(
    "object_index",
    [
        0x30,  # Weird 30-Degree Hill
        0x3A,
        0x70,  # 30 Degree Hill - Up/Left
        0x7A,
        0xB0,  # 30 Degree Underwater Hill - Up/Left
        0xBA,
    ],
)
def test_object_rendering_4_2(object_index, qtbot):
    object_factory = LevelObjectFactory(HILLY_OBJECT_SET, HILLY_GRAPHICS_SET, 0, [], False)

    object_domain = 0x03
    level_object = object_factory.from_properties(object_domain, object_index, 0, 0, None, 0)

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
    "object_set, graphics_set",
    list(
        zip(
            range(PLAINS_OBJECT_SET, UNDERGROUND_OBJECT_SET + 1),
            range(PLAINS_GRAPHICS_SET, UNDERGROUND_GRAPHICS_SET + 1),
        )
    ),
)
def test_ending_object(object_set, graphics_set, qtbot):
    object_factory = LevelObjectFactory(object_set, graphics_set, 0, [], False)

    ending_object = object_factory.from_properties(0x2, 0x09, 0, 0, None, 0)

    _test_object_against_reference(ending_object, qtbot)
