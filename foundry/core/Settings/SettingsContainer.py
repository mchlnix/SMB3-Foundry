
import collections.abc as collections
import logging
from typing import Dict, Any, Callable, Hashable

from ..Action.Action import Action
from .Setting import Setting
from foundry import log_dir
from foundry.core.util import default_settings_dir


SETTING_CONTAINER_FLAG = "IS SETTING CONTAINER"


_logger = logging.getLogger(__name__)
_logger.setLevel(logging.WARNING)
_handler = logging.FileHandler(f"{log_dir}/setting_container.log")
_formatter = logging.Formatter('%(asctime)s | %(name)s |  %(levelname)s: %(message)s')
_handler.setFormatter(_formatter)
_logger.addHandler(_handler)


class SettingsContainer:
    """A state that stores easy to save data, typically containing primitives and other setting containers"""
    settings: "Dict[str: Setting]"
    settings_containers: 'Dict[str: "SettingsContainer"]'

    SETTING_DIR = default_settings_dir

    def __init__(self, name: str, settings: "Dict[str: Any]" = None) -> None:
        self.name = name
        self.settings_states = {} if settings is None else settings
        self.settings = {}
        self.settings_containers = {}
        _logger.debug(f"{self} was created")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name}, settings{self.settings_states})"

    @classmethod
    def from_json_file(cls, name: str, base_dir: str, force: bool = False) -> "SettingsContainer":
        """Loads a container from a file"""
        import json
        try:
            with open(f"{base_dir}/{name}", "r") as settings_file:
                return cls(name, json.loads(settings_file.read()))
        except json.JSONDecodeError:
            if force:
                return cls(name, {})
            else:
                raise json.JSONDecodeError
        except FileNotFoundError:
            if force:
                return cls(name, {})
            else:
                raise FileNotFoundError

    def save_to_json(self, base_dir: str) -> None:
        """Saves the settings to json"""
        import json
        with open(f"{base_dir}/{self.name}", "w+") as settings_file:
            settings_file.write(json.dumps(self.settings_states, indent=4, sort_keys=True))
        for key in self.settings_containers:
            self.settings_containers[key]().save_to_json(base_dir)

    def get_setting_container(self, name: str) -> "SettingsContainer":
        """Returns a given setting"""
        _logger.debug(f"{self} getting container with name {name}")
        if name not in self.settings_containers:
            # Try and create a setting container if it doesn't exist
            if name not in self.settings_states:
                _logger.warning(f"{name} is not inside {self}")
                raise KeyError(f"{name} is not a setting inside {self}")
            else:
                self._create_setting_container(name)
        return self.settings_containers[name]()

    def safe_get_setting(self, name: str, default_value: Hashable) -> Hashable:
        """Returns a given setting no matter what"""
        try:
            return self.get_setting(name)
        except KeyError:
            self.set_setting(name, default_value)
            return self.get_setting(name)

    def get_setting(self, name: str) -> Hashable:
        """Returns a given setting"""
        _logger.debug(f"{self} getting setting with name {name}")
        if name not in self.settings:
            # Try and create a setting if it doesn't exist
            if name not in self.settings_states:
                _logger.warning(f"{name} is not inside {self}")
                raise KeyError(f"{name} is not a setting")
            else:
                self._create_setting(name)
        return self.settings_states[name]

    def set_setting(self, name: str, value: Hashable) -> None:
        """Sets a setting to a specific state"""
        if not isinstance(value, collections.Hashable):
            _logger.warning(f"Failed to add {value} to {name} because it is not hashable")
            raise TypeError(f"{value} is not hashable")

        _logger.debug(f"{self} setting {value} to {name}")
        if name not in self.settings:
            if name not in self.settings_states:
                self.settings_states.update({name: value})
            self._create_setting(name)
        self.settings[name]().state = value

    def set_setting_container(self, name: str, container: "SettingsContainer") -> None:
        """Sets a setting container"""
        _logger.debug(f"{self} setting {container} to {name}")
        self.settings_states.update({name: SETTING_CONTAINER_FLAG})
        self.settings_containers.update({name: lambda: container})

    def observe_setting(self, name: str, receiver: Callable) -> None:
        """Adds an observer to a setting"""
        _logger.debug(f"{self} attaching observer to Setting {name}")
        if name not in self.settings:
            if name not in self.settings_states:
                _logger.warning(f"{name} is not a setting inside {self}")
                raise KeyError(f"{name} is not a setting")
            self._create_setting(name)

        self.settings_states[name]().observer.attach_observer(lambda value: receiver(value))

    def _create_setting(self, name: str) -> None:
        _logger.debug(f"{self} initializing setting with {name}")
        if isinstance(state := self.settings_states[name], dict):
            _logger.warning(f"{name} is not a setting inside {self}")
            raise AttributeError(f"Cannot initialize {name} with data {state} as Setting")
        setting = Setting(name, state, lambda value: self.settings_states.__setitem__(name, value), Action)
        self.settings.update({name: lambda: setting})  # makes a reference to the setting that is hashable

    def _create_setting_container(self, name: str) -> None:
        _logger.debug(f"{self} initializing setting container with {name}")
        if SETTING_CONTAINER_FLAG != self.settings_states[name]:
            _logger.warning(f"{name} is not a setting container inside {self}")
            raise AttributeError(f"{name} is not a SettingsContainer")
        setting_container = SettingsContainer.from_json_file(name, self.SETTING_DIR, True)
        self.settings_containers.update({name: lambda: setting_container})








