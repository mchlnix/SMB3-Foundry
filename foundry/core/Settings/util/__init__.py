

from typing import Hashable, Callable, Dict

from foundry.core.Settings.SettingsContainer import SettingsContainer
from foundry.core.util import default_settings_dir


default_settings_dir.mkdir(parents=True, exist_ok=True)


_main_container = SettingsContainer.from_json_file("main", default_settings_dir, True)


def observe_setting(name: str, default_value: Hashable, observer: Callable) -> None:
    """Observes a setting"""
    if name not in _main_container.settings_states:
        _main_container.set_setting(name, default_value)
    _main_container.observe_setting(name, observer)


def get_setting(name: str, default_value: Hashable) -> Hashable:
    """Gets the correct setting or returns the default value"""
    if name not in _main_container.settings_states:
        _main_container.set_setting(name, default_value)
    return _main_container.get_setting(name)


def set_setting(name: str, value: Hashable) -> None:
    """Sets the correct setting or creates it"""
    _main_container.set_setting(name, value)


def load_settings():
    """Loads the known settings"""


def convert_settings(settings: Dict) -> dict:
    """Converts settings to a dictionary for json"""
    dic = {}
    for key, setting in settings.items():
        dic.update({key: setting.state})
    return dic


def save_settings():
    """Saves the settings"""
    _main_container.save_to_json(default_settings_dir)