from os import chdir

import pytest

from foundry.game.File import ROM


@pytest.fixture(scope="session", autouse=True)
def cd_to_repo_root():
    chdir("..")


@pytest.fixture(scope="session")
def rom():
    ROM.load_from_file("SMB3.nes")

    yield ROM()
