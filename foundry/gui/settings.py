from typing import Callable

import qdarkstyle
from PySide6.QtCore import QSettings

RESIZE_LEFT_CLICK = "LMB"
RESIZE_RIGHT_CLICK = "RMB"

GUI_STYLE: dict[str, Callable] = {
    "RETRO": lambda: "",  # noqa
    "DRACULA": qdarkstyle.load_stylesheet_pyside6,
}


class ASMLoadingBehavior:
    DONT_ASK = 0
    ASK_IF_NEEDED = 1
    LOAD_IF_AVAILABLE = 2


class ReleaseChannel:
    NONE = 0
    STABLE = 1
    NIGHTLY = 2


# TODO Make into an enum?
SETTINGS: dict[str, str | int | float | bool] = dict()
SETTINGS["editor/instaplay_emulator"] = "fceux"
SETTINGS["editor/instaplay_arguments"] = "%f"
SETTINGS["editor/instaplay_skip_title_screen"] = True
SETTINGS["editor/object_scroll_enabled"] = False
SETTINGS["editor/default_powerup"] = 0
SETTINGS["editor/powerup_starman"] = False

SETTINGS["editor/resize_mode"] = RESIZE_LEFT_CLICK
SETTINGS["editor/gui_style"] = ""  # initially blank, since we can't call load_stylesheet until the app is started
SETTINGS["editor/default_dir"] = "User"
SETTINGS["editor/default_dir_path"] = ""
SETTINGS["editor/custom_default_dir_path"] = ""
SETTINGS["editor/show_block_item_in_toolbar"] = True
SETTINGS["editor/ask_for_level_management"] = True
SETTINGS["editor/auto_save_enabled"] = True
SETTINGS["editor/asm_loading_behavior"] = ASMLoadingBehavior.ASK_IF_NEEDED
SETTINGS["editor/remember_last_level"] = False
SETTINGS["editor/remember_last_level_path"] = ""
SETTINGS["editor/remember_last_level_object_set"] = 0
SETTINGS["editor/remember_last_level_lvl_address"] = 0
SETTINGS["editor/remember_last_level_enemy_address"] = 0
SETTINGS["editor/remember_last_level_world_number"] = 1
SETTINGS["editor/monitor_rom_for_changes"] = True

SETTINGS["editor/asked_for_startup"] = False
SETTINGS["editor/release_channel"] = ReleaseChannel.NIGHTLY
SETTINGS["editor/version_to_ignore"] = ""

SETTINGS["editor/settings_version"] = 0

SETTINGS["level_view/draw_mario"] = True
SETTINGS["level_view/draw_jumps"] = False
SETTINGS["level_view/draw_grid"] = False
SETTINGS["level_view/draw_grid_coordinates"] = False
SETTINGS["level_view/draw_expansion"] = False
SETTINGS["level_view/draw_jump_on_objects"] = True
SETTINGS["level_view/draw_items_in_blocks"] = True
SETTINGS["level_view/draw_invisible_items"] = True
SETTINGS["level_view/draw_autoscroll"] = False
SETTINGS["level_view/block_transparency"] = True
SETTINGS["level_view/block_animation"] = True
SETTINGS["level_view/special_background"] = True
SETTINGS["level_view/object_tooltip_enabled"] = True
SETTINGS["level_view/last_zoom_factor"] = 1.0


_settings: dict[str, str | int | float | bool] = {
    "world_view/show_grid": False,
    "world_view/show_border": False,
    "world_view/animated_tiles": True,
    "world_view/show_level_pointers": True,
    "world_view/show_level_previews": False,
    "world_view/show_sprites": True,
    "world_view/show_start_position": False,
    "world_view/show_airship_paths": 0,
    "world_view/show_pipes": False,
    "world_view/show_locks": False,
}
_settings.update(SETTINGS)


class Settings(QSettings):
    def __init__(self, organization="mchlnix", application="default"):
        super(Settings, self).__init__(organization, application)

        for key, default_value in _settings.items():
            if self.value(key) is None or self.is_default:
                self.setValue(key, default_value)

        self.sync()

        self.update_by_version()

    @property
    def is_default(self):
        return self.organizationName() == "mchlnix" and self.applicationName() == "default"

    def value(self, key: str, default_value=None, type_=None):
        if key in _settings and type_ is None:
            type_ = type(_settings[key])

        returned_value = super(Settings, self).value(key, default_value)

        if returned_value is None:
            return returned_value
        elif type_ is bool and isinstance(returned_value, str):
            # boolean values loaded from disk are returned as strings for some reason
            return returned_value.lower() == "true"
        elif type_ is None:
            return returned_value
        else:
            return type_(returned_value)

    def setValue(self, key: str, value):
        return super(Settings, self).setValue(key, value)

    def sync(self):
        if self.is_default:
            return None

        return super(Settings, self).sync()

    def update_by_version(self):
        if self.applicationName() == "foundry":
            self._update_foundry_by_version()

    def _update_foundry_by_version(self):
        while True:
            settings_version = self.value("editor/settings_version")

            if settings_version == 0:
                self.setValue("world_view/show_level_pointers", True)

                self.setValue("editor/settings_version", settings_version + 1)
                continue

            if settings_version == 1:
                self.setValue("editor/settings_version", settings_version + 1)

                for key in self.allKeys():
                    if " " not in key:
                        continue

                    underscore_key = key.replace(" ", "_")

                    if underscore_key in _settings:
                        self.setValue(underscore_key, self.value(key))

                    self.remove(key)

            if settings_version == 2:
                self.setValue("editor/settings_version", settings_version + 1)

                # preserve the setting to not check updates on startup
                if not self.value("editor/update_on_startup", default_value=True):
                    self.setValue("editor/release_channel", ReleaseChannel.NONE)

                self.remove("editor/update_on_startup")
                continue
            break
