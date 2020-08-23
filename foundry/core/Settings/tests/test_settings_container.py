

from foundry.core.Settings.SettingsContainer import SettingsContainer


def test_initialization():
    """Tests if the setting container can initialize"""
    SettingsContainer("test")


def test_initialized_settings():
    """Tests if settings are loaded from initialization"""
    container = SettingsContainer("test", {"test_setting": True})
    assert container.get_setting("test_setting")


def test_getting_setting():
    """Tests getting a setting"""
    container = SettingsContainer("test", {"test_setting": True})
    assert container.get_setting("test_setting")


def test_setting_setting():
    """Tests setting of already existing setting"""
    container = SettingsContainer("test", {"test_setting": False})
    container.set_setting("test_setting", True)
    assert container.get_setting("test_setting")


def test_setting_new_setting():
    """Tests the creation of a setting"""
    container = SettingsContainer("test")
    container.set_setting("test_setting", True)
    assert container.get_setting("test_setting")


def test_setting_new_container():
    """Tests the setting of a setting container"""
    container = SettingsContainer("test")
    container.set_setting_container("new_setting_container", SettingsContainer("other_container"))
    assert "new_setting_container" in container.settings_states


def test_getting_container():
    """Tests getting a container"""
    container = SettingsContainer("test")
    container.set_setting_container("new_setting_container", SettingsContainer("other_container"))
    other_container = container.get_setting_container("new_setting_container")
    assert other_container.name == "other_container"
