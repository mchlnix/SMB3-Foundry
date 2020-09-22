import qdarkstyle

from foundry.core.Settings.util import get_setting
from foundry.core.util import RETRO_STYLE_SET, DRACULA_STYLE_SET


def get_gui_style():
    if get_setting("gui_style", RETRO_STYLE_SET) == DRACULA_STYLE_SET:
        return qdarkstyle.load_stylesheet()