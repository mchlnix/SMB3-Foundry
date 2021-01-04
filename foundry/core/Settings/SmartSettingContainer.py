

from typing import Dict, Any, Hashable

from foundry.core.util import default_settings_dir
from foundry.core.Settings.SettingsContainer import SettingsContainer

class SmartSettingContainer(SettingsContainer):
    """A SettingContainer with the auto save functionality"""

    def __init__(self, name: str, path: str, settings: "Dict[str: Any]" = None) -> None:
        super().__init__(name, settings)
        self.path = path

    @classmethod
    def from_json_file(cls, name: str, base_dir: str = default_settings_dir, force: bool = False) -> "SettingsContainer":
        import json
        try:
            with open(f"{base_dir}/{name}", "r") as settings_file:
                return cls(name, f"{base_dir}/{name}", json.loads(settings_file.read()))
        except json.JSONDecodeError:
            if force:
                return cls(name, f"{base_dir}/{name}", {})
            else:
                raise json.JSONDecodeError
        except FileNotFoundError:
            if force:
                return cls(name, f"{base_dir}/{name}", {})
            else:
                raise FileNotFoundError

    def set_setting(self, name: str, value: Hashable) -> None:
        super().set_setting(name, value)
        self.save_to_json(self.path)

    def set_setting_container(self, name: str, container: "SettingsContainer") -> None:
        super().set_setting_container(name, container)
        self.save_to_json(self.path)
