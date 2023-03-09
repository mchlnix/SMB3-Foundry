from random import seed

import pytest


@pytest.fixture(scope="session", autouse=True)
def seed_random():
    seed(0)
