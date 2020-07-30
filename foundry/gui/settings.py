import json
import pathlib
from typing import Union, Callable

from foundry.core.ObservableDecorator import Observable

RESIZE_LEFT_CLICK = "LMB"
RESIZE_RIGHT_CLICK = "RMB"
DRACULA_STYLE_SET = "DRACULA"
RETRO_STYLE_SET = "RETRO"
"""
SETTINGS = dict()
SETTINGS["instaplay_emulator"] = "fceux"
SETTINGS["instaplay_arguments"] = "%f"

SETTINGS["resize_mode"] = RESIZE_LEFT_CLICK
SETTINGS["gui_style"] = DRACULA_STYLE_SET

SETTINGS["draw_mario"] = True
SETTINGS["draw_jumps"] = False
SETTINGS["draw_grid"] = False
SETTINGS["draw_expansion"] = False
SETTINGS["draw_jump_on_objects"] = True
SETTINGS["draw_items_in_blocks"] = True
SETTINGS["draw_invisible_items"] = True
SETTINGS["block_transparency"] = True
SETTINGS["background_enabled"] = False

SETTINGS["visual_object_toolbar"] = True
SETTINGS["object_attribute_toolbar"] = True
SETTINGS["compact_object_toolbar"] = True
SETTINGS["bytes_counter_toolbar"] = True
SETTINGS["object_list_toolbar"] = True
"""

default_settings_dir = pathlib.Path.home() / ".smb3foundry"
default_settings_dir.mkdir(parents=True, exist_ok=True)

default_settings_path = default_settings_dir / "settings"
SETTINGS = {}


class Setting:
    """A setting that can automatically update all observers when changed"""
    def __init__(self, name: str, value: Union[bool, int, float, str]) -> None:
        self.action = Observable(self.action)
        self.name = name
        self._value = value

    @property
    def value(self) -> Union[bool, int, float, str]:
        """The value of the setting"""
        return self._value

    @value.setter
    def value(self, value: Union[bool, int, float, str]) -> None:
        self._value = value

    def add_observer(self, observer: Callable) -> None:
        """Adds an observer"""
        self.action.attach_observer(observer)

    def action(self) -> Union[bool, int, float, str]:
        """Updates all the observers"""
        return self.value


def watch_setting(name: str, default_value: Union[bool, int, float, str], observer: Callable) -> None:
    """Observes a setting"""
    if name not in SETTINGS:
        SETTINGS.update({name: Setting(name, default_value)})
    SETTINGS[name].value.attach_observer(observer)


def get_setting(name: str, default_value: Union[bool, int, float, str]) -> Union[bool, int, float, str]:
    """Gets the correct setting or returns the default value"""
    if name not in SETTINGS:
        SETTINGS.update({name: Setting(name, default_value)})
    return SETTINGS[name].value


def set_setting(name: str, value: Union[bool, int, float, str]) -> None:
    """Sets the correct setting or creates it"""
    if value is None:
        raise NotImplementedError
    print(name, value)
    if name not in SETTINGS:
        SETTINGS.update({name: Setting(name, value)})
    else:
        SETTINGS[name].value = value


def load_settings():
    """Loads the known settings"""
    if not default_settings_path.exists():
        return

    try:
        with open(str(default_settings_path), "r") as settings_file:
            settings_dict = json.loads(settings_file.read())
    except json.JSONDecodeError:
        return

    for key, value in settings_dict.items():
        SETTINGS.update({key: Setting(key, value)})


def convert_settings(settings) -> dict:
    """Converts settings to a dictionary for json"""
    dic = {}
    for key, setting in settings.items():
        dic.update({key: setting.value})
    return dic


def save_settings():
    """Saves the settings"""
    with open(str(default_settings_path), "w") as settings_file:
        settings_file.write(json.dumps(convert_settings(SETTINGS), indent=4, sort_keys=True))
