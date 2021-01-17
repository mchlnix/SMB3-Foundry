import json
import qdarkstyle

from foundry import default_settings_path

RESIZE_LEFT_CLICK = "LMB"
RESIZE_RIGHT_CLICK = "RMB"

GUI_STYLE = {
    "RETRO": lambda: "",
    "DRACULA": qdarkstyle.load_stylesheet,
}

SETTINGS = dict()
SETTINGS["instaplay_emulator"] = "fceux"
SETTINGS["instaplay_arguments"] = "%f"
SETTINGS["default_powerup"] = 0

SETTINGS["resize_mode"] = RESIZE_LEFT_CLICK
SETTINGS["gui_style"] = ""  # initially blank, since we can't call load_stylesheet until the app is started

SETTINGS["draw_mario"] = True
SETTINGS["draw_jumps"] = False
SETTINGS["draw_grid"] = False
SETTINGS["draw_expansion"] = False
SETTINGS["draw_jump_on_objects"] = True
SETTINGS["draw_items_in_blocks"] = True
SETTINGS["draw_invisible_items"] = True
SETTINGS["draw_autoscroll"] = False
SETTINGS["block_transparency"] = True
SETTINGS["object_scroll_enabled"] = False


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
