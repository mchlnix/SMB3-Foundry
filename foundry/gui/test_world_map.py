import os
from pathlib import Path

import pytest

from foundry.conftest import compare_images
from foundry.game.level.WorldMap import WorldMap
from foundry.gui.WorldMapView import WorldMapView
from smb3parse.levels import WORLD_COUNT

reference_image_dir = Path(__file__).parent.joinpath("test_refs")
os.makedirs(reference_image_dir, exist_ok=True)


@pytest.mark.parametrize("world_number", list(range(1, WORLD_COUNT + 1)))
def test_world_map_drawing(world_number, qtbot):
    world_map = WorldMap(world_number)

    view = WorldMapView(None, world_map)
    view.resize(view.sizeHint())

    qtbot.addWidget(view)

    image_name = f"world_map_{world_number}.png"
    reference_image_path = str(reference_image_dir.joinpath(image_name))

    compare_images(image_name, reference_image_path, view.grab())
