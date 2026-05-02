"""Pytest fixtures shared by visualization localization tests."""

from collections.abc import Callable

import pytest

from foundry.gui.localization import reload_available_languages
from foundry.gui.settings import Settings


@pytest.fixture
def settings_factory() -> Callable[[str], Settings]:

    def create_settings(application: str) -> Settings:
        settings = Settings("mchlnix-test", application)
        settings.clear()
        return Settings("mchlnix-test", application)

    return create_settings


@pytest.fixture
def temporary_translation_dir(monkeypatch, tmp_path):
    monkeypatch.setenv("FOUNDRY_USER_TRANSLATION_DIR", str(tmp_path))
    reload_available_languages()
    yield tmp_path
    monkeypatch.delenv("FOUNDRY_USER_TRANSLATION_DIR", raising=False)
    reload_available_languages()
