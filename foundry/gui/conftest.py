from pathlib import Path

import pytest

from foundry.game.File import ROM


@pytest.fixture(scope="module", autouse=True)
def rom():
    current_dir = Path(__file__).parent

    # go up 2 levels

    repo_root = current_dir.parent.parent

    rom_path = repo_root.joinpath("SMB3.nes")

    rom = ROM(rom_path)

    yield rom
