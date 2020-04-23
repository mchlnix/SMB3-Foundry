import pytest

from foundry.conftest import level_1, level_1_1_enemy_address, level_1_1_object_address, world_1
from foundry.gui.MainWindow import MainWindow
from smb3parse.objects.object_set import PLAINS_OBJECT_SET


@pytest.fixture
def main_window(qtbot):
    # mock the rom loading, since it is a modal dialog. the rom is loaded in conftest.py
    MainWindow.on_open_rom = mocked_open_rom_and_level_select
    MainWindow.showMaximized = lambda _: None  # don't open automatically
    MainWindow.safe_to_change = lambda _: True  # don't ask for confirmation on changed level

    main_window = MainWindow()

    qtbot.addWidget(main_window)

    return main_window


def mocked_open_rom_and_level_select(self: MainWindow, _):
    self.update_level(world_1, level_1, level_1_1_object_address, level_1_1_enemy_address, PLAINS_OBJECT_SET)

    return True
