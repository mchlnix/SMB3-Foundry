import json
import pathlib

RESIZE_LEFT_CLICK = "LMB"
RESIZE_RIGHT_CLICK = "RMB"

SETTINGS = dict()
SETTINGS["instaplay_emulator"] = "fceux"
SETTINGS["instaplay_arguments"] = "%f"

SETTINGS["resize_mode"] = RESIZE_LEFT_CLICK

SETTINGS["draw_mario"] = True
SETTINGS["draw_jumps"] = False
SETTINGS["draw_grid"] = False
SETTINGS["draw_expansion"] = False
SETTINGS["draw_jump_on_objects"] = True
SETTINGS["draw_items_in_blocks"] = True
SETTINGS["draw_invisible_items"] = True
SETTINGS["block_transparency"] = True
SETTINGS["object_scroll_enabled"] = False

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
        settings_file.write(json.dumps(SETTINGS, indent=4, sort_keys=True))
