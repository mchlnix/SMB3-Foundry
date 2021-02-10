from os import chdir
from pathlib import Path

import pytest

from smb3parse.levels.world_map import WorldMap
from smb3parse.util.rom import Rom, INESHeader

root_dir = Path(__file__).parent.parent.parent

test_rom_path = root_dir / Path("SMB3.nes")
assert test_rom_path.exists(), f"The test suite needs a SMB3(U) Rom at '{test_rom_path}' to run."


@pytest.fixture(scope="session", autouse=True)
def cd_to_repo_root():
    chdir(root_dir)


@pytest.fixture()
def rom():
    if not test_rom_path.exists():
        raise ValueError(
            f"To run the test suite, place a US SMB3 Rom named '{test_rom_path}' in the root of the repository."
        )

    with open(test_rom_path, "rb") as rom_file:
        data = bytearray(rom_file.read())
        yield Rom(data, INESHeader.from_buffer_copy(data))


@pytest.fixture
def world_1(rom):
    return WorldMap.from_world_number(rom, 1)


@pytest.fixture
def world_8(rom):
    return WorldMap.from_world_number(rom, 8)
