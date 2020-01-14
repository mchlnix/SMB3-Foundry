import os
from pathlib import Path

import pytest
from PySide2.QtGui import QImage
from pytest import fail, skip

from foundry.game.gfx.objects.LevelObjectFactory import LevelObjectFactory
from foundry.gui.ObjectViewer import ObjectDrawArea
from smb3parse.objects.object_set import HILLY_GRAPHICS_SET, HILLY_OBJECT_SET

reference_image_dir = Path(__file__).parent.joinpath("test_refs")
os.makedirs(reference_image_dir, exist_ok=True)


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

    view = ObjectDrawArea(None, HILLY_GRAPHICS_SET, HILLY_GRAPHICS_SET)

    qtbot.addWidget(view)

    view.update_object(level_object)

    view.setGeometry(0, 0, *level_object.display_size().toTuple())

    image_name = f"object_set_{HILLY_OBJECT_SET}_domain_{object_domain}_index_{hex(object_index)}.png"
    image_path = str(reference_image_dir.joinpath(image_name))

    if os.path.exists(image_path):
        ref_image = QImage(image_path)

        if view.grab().toImage() != ref_image:
            view.show()

            qtbot.waitForWindowShown(view)

            qtbot.stopForInteraction()

            fail(f"{image_name} did not look like the reference.")
        else:
            return  # pass the test

    else:
        view.grab().toImage().save(image_path)

        skip(f"No ref image was found. Saved new ref under {image_path}.")
