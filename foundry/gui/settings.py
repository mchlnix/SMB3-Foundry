import json
from typing import Union, Callable, Dict

from foundry.core.Action.Action import Action
from foundry.core.State.State import State
from foundry.core.util import default_settings_dir, default_settings_path

default_settings_dir.mkdir(parents=True, exist_ok=True)

SETTINGS = {}


def observe_setting(name: str, default_value: Union[bool, int, float, str], observer: Callable) -> None:
    """Observes a setting"""
    if name not in SETTINGS:
        SETTINGS.update({name: State(name, default_value, Action)})
    SETTINGS[name].observer.attach_observer(observer)


def get_setting(name: str, default_value: Union[bool, int, float, str]) -> Union[bool, int, float, str]:
    """Gets the correct setting or returns the default value"""
    if name not in SETTINGS:
        SETTINGS.update({name: State(name, default_value, Action)})
    return SETTINGS[name].state


def set_setting(name: str, value: Union[bool, int, float, str]) -> None:
    """Sets the correct setting or creates it"""
    if value is None:
        raise NotImplementedError
    print(name, value)
    if name not in SETTINGS:
        SETTINGS.update({name: State(name, value, Action)})
    else:
        SETTINGS[name].state = value


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
        set_setting(key, value)


def convert_settings(settings: Dict) -> dict:
    """Converts settings to a dictionary for json"""
    dic = {}
    for key, setting in settings.items():
        dic.update({key: setting.state})
    return dic


def save_settings():
    """Saves the settings"""
    with open(str(default_settings_path), "w") as settings_file:
        settings_file.write(json.dumps(convert_settings(SETTINGS), indent=4, sort_keys=True))
