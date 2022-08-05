from functools import partial
from typing import Callable, Dict, Union

import qdarkstyle
from PySide6.QtCore import QSettings

RESIZE_LEFT_CLICK = "LMB"
RESIZE_RIGHT_CLICK = "RMB"

GUI_STYLE: Dict[str, Callable] = {
    "RETRO": lambda: "",
    "DRACULA": partial(qdarkstyle.load_stylesheet, pyside=True),
}

SETTINGS: Dict[str, Union[str, int, bool]] = dict()
SETTINGS["editor/instaplay_emulator"] = "fceux"
SETTINGS["editor/instaplay_arguments"] = "%f"
SETTINGS["editor/object_scroll_enabled"] = False
SETTINGS["editor/default_powerup"] = 0

SETTINGS["editor/resize_mode"] = RESIZE_LEFT_CLICK
SETTINGS["editor/gui_style"] = ""  # initially blank, since we can't call load_stylesheet until the app is started
SETTINGS["editor/default dir"] = "User"
SETTINGS["editor/default dir path"] = ""
SETTINGS["editor/custom default dir path"] = ""
SETTINGS["editor/show_block_item_in_toolbar"] = True

SETTINGS["level view/draw_mario"] = True
SETTINGS["level view/draw_jumps"] = False
SETTINGS["level view/draw_grid"] = False
SETTINGS["level view/draw_expansion"] = False
SETTINGS["level view/draw_jump_on_objects"] = True
SETTINGS["level view/draw_items_in_blocks"] = True
SETTINGS["level view/draw_invisible_items"] = True
SETTINGS["level view/draw_autoscroll"] = False
SETTINGS["level view/block_transparency"] = True
SETTINGS["level view/special_background"] = True
SETTINGS["level view/object_tooltip_enabled"] = True


_settings: Dict[str, Union[str, int, bool]] = {
    "world view/show grid": False,
    "world view/show border": False,
    "world view/show level pointers": False,
    "world view/show level previews": False,
    "world view/show sprites": True,
    "world view/show start position": False,
    "world view/show airship paths": 0,
    "world view/show pipes": False,
    "world view/show locks": False,
}
_settings.update(SETTINGS)


class Settings(QSettings):
    def __init__(self, organization="mchlnix", application="default"):
        super(Settings, self).__init__(organization, application)

        for key, default_value in _settings.items():
            if self.value(key) is None or self.is_default:
                self.setValue(key, default_value)

        self.sync()

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
            return returned_value == "true"
        elif type_ is None:
            return returned_value
        else:
            return type_(returned_value)

    def setValue(self, key: str, value):
        return super(Settings, self).setValue(key, value)

    def sync(self):
        if self.is_default:
            return
        else:
            return super(Settings, self).sync()
