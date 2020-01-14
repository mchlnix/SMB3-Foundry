from pathlib import Path

import pytest

from foundry.game.File import ROM

world_1, level_1 = 1, 1
level_1_1_object_address = 0x1FB92
level_1_1_enemy_address = 0xC537 + 1


@pytest.fixture(scope="module", autouse=True)
def rom():
    current_dir = Path(__file__).parent

    repo_root = current_dir.parent

    rom_path = repo_root.joinpath("SMB3.nes")

    rom = ROM(rom_path)

    yield rom
