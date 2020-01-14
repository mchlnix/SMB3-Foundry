import pytest

from foundry.gui.MainWindow import MainWindow
from foundry.conftest import level_1, level_1_1_enemy_address, level_1_1_object_address, object_set_plains, world_1


@pytest.fixture
def main_window(qtbot):
    # mock the rom loading, since it is a modal dialog. the rom is loaded in conftest.py
    MainWindow.on_open_rom = mocked_open_rom_and_level_select
    MainWindow.showMaximized = lambda: None  # don't open automatically

    main_window = MainWindow()

    qtbot.addWidget(main_window)

    return main_window


def mocked_open_rom_and_level_select(self: MainWindow):
    self.update_level(world_1, level_1, level_1_1_object_address, level_1_1_enemy_address, object_set_plains)

    return True


def test_open(main_window):
    pass
