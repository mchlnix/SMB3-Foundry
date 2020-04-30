import json
import pathlib
from collections import defaultdict

SETTINGS = defaultdict(str)
SETTINGS["instaplay_emulator"] = "fceux"
SETTINGS["instaplay_arguments"] = "%f"

default_settings_dir = pathlib.Path.home() / ".smb3foundry"
default_settings_dir.mkdir(parents=True, exist_ok=True)

default_settings_path = default_settings_dir / "settings"


def load_settings():
    if not default_settings_path.exists():
        return

    try:
        with open(str(default_settings_path), "r") as settings_file:
            settings_dict = json.loads(settings_file.read())
    except json.JSONDecodeError:
        return

    SETTINGS.update(settings_dict)


def save_settings():
    with open(str(default_settings_path), "w") as settings_file:
        settings_file.write(json.dumps(SETTINGS))
