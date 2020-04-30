from os import chdir
from pathlib import Path

import pytest

from smb3parse.levels.world_map import WorldMap
from smb3parse.util.rom import Rom


@pytest.fixture(scope="session", autouse=True)
def cd_to_repo_root():
    chdir(Path(__file__).parent.parent.parent)


@pytest.fixture()
def rom():
    with open("SMB3.nes", "rb") as rom_file:
        yield Rom(bytearray(rom_file.read()))


@pytest.fixture
def world_1(rom):
    return WorldMap.from_world_number(rom, 1)


@pytest.fixture
def world_8(rom):
    return WorldMap.from_world_number(rom, 8)
