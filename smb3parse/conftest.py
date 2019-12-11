import os
from os import chdir

import pytest

from util.rom import Rom


@pytest.fixture(scope="session", autouse=True)
def cd_to_repo_root():
    chdir(os.path.dirname(__file__) + "/..")


@pytest.fixture(scope="session")
def rom():
    with open("SMB3.nes", "rb") as rom_file:
        yield Rom(bytearray(rom_file.read()))
