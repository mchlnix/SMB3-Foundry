import sys
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, cast

from PySide6.QtCore import QBuffer, QIODevice, QUrl
from PySide6.QtGui import QDesktopServices, QIcon, QPixmap, Qt, QUndoCommand, QUndoStack
from PySide6.QtWidgets import QApplication, QWidget

from foundry.gui.settings import Settings
from smb3parse.constants import DESERT_OBJECT_SET
from smb3parse.util import apply

if TYPE_CHECKING:
    from foundry.game.level import EnemyItemAddress, LevelAddress

root_dir = Path(__file__).parent.parent

home_dir = Path.home() / ".smb3foundry"
home_dir.mkdir(parents=True, exist_ok=True)

default_settings_path = home_dir / "settings"

auto_save_path = home_dir / "auto_save"
auto_save_path.mkdir(parents=True, exist_ok=True)

auto_save_rom_path = auto_save_path / "auto_save.nes"
auto_save_m3l_path = auto_save_path / "auto_save.m3l"
auto_save_level_data_path = auto_save_path / "level_data.json"

data_dir = root_dir.joinpath("data")
doc_dir = root_dir.joinpath("doc")
icon_dir = data_dir.joinpath("icons")

releases_link = "https://github.com/mchlnix/SMB3-Foundry/releases"
feature_video_link = "https://www.youtube.com/watch?v=7_22cAffMmE"
github_link = "https://github.com/mchlnix/SMB3-Foundry"
github_issue_link = "https://github.com/mchlnix/SMB3-Foundry/issues"
discord_link = "https://discord.gg/pm87gm7"

enemy_compat_link = QUrl.fromLocalFile(str(doc_dir.joinpath("SMB3 enemy compatibility.html")))

ROM_FILE_FILTER = "ROM files (*.nes *.rom);;All files (*)"
M3L_FILE_FILTER = "M3L files (*.m3l);;All files (*)"
ASM_FILE_FILTER = "ASM files (*.asm);;All files (*)"
SMB3_ASM_FILE_FILTER = "smb3.asm (smb3.asm);;ASM files (*.asm);;All files (*)"
FNS_FILE_FILTER = "FNS files (*.fns);;All files (*)"
IMG_FILE_FILTER = "Screenshots (*.png);;All files (*)"

NO_PARENT = cast(QWidget, cast(object, None))


def ctrl_is_pressed():
    """Handle ctrl is pressed.

    It provides shared behavior used by the editor runtime. The return value exposes the computed state expected by callers.

    Returns
    -------
    Any
        True when the Ctrl modifier is pressed.
    """
    return bool(QApplication.keyboardModifiers() & Qt.KeyboardModifier.ControlModifier)


def shift_is_pressed():
    """Handle shift is pressed.

    It provides shared behavior used by the editor runtime. The return value exposes the computed state expected by callers.

    Returns
    -------
    Any
        True when the Shift modifier is pressed.
    """
    return bool(QApplication.keyboardModifiers() & Qt.KeyboardModifier.ShiftModifier)


def open_url(url: str | QUrl):
    """Open url.

    It provides shared behavior used by the editor runtime. The method delegates lower-level work while keeping the public workflow focused.

    Parameters
    ----------
    url : str | QUrl
        Url used by the operation.
    """
    QDesktopServices.openUrl(QUrl(url))


def is_pyinstalled() -> bool:
    """Return whether pyinstalled.

    It provides shared behavior used by the editor runtime. The return value exposes the computed state expected by callers.

    Returns
    -------
    bool
        Whether the requested condition is true.
    """
    return hasattr(sys, "_MEIPASS")


def is_nightly_version():
    """Return whether nightly version.

    It provides shared behavior used by the editor runtime. The return value exposes the computed state expected by callers.

    Returns
    -------
    Any
        Whether the requested condition is true.
    """
    return get_current_version_name().startswith("nightly")


def get_current_version_name() -> str:
    """Return current version name.

    It provides shared behavior used by the editor runtime. The lookup centralizes coordinate or identifier handling for callers.

    Returns
    -------
    str
        The requested current version name.

    Raises
    ------
    LookupError
        If the requested data cannot be found.
    """
    version_file = root_dir / "VERSION"

    if not version_file.exists():
        raise LookupError("Version file not found.")

    return version_file.read_text().strip()


@lru_cache(256)
def icon(icon_name: str):
    """Handle icon.

    It provides shared behavior used by the editor runtime. The return value exposes the computed state expected by callers.

    Parameters
    ----------
    icon_name : str
        Icon name used by the operation.

    Returns
    -------
    Any
        Icon loaded from the application resources.

    Raises
    ------
    FileNotFoundError
        If the expected file cannot be found.
    """
    icon_path = icon_dir / icon_name
    data_path = data_dir / icon_name

    if icon_path.exists():
        return QIcon(str(icon_path))
    elif data_path.exists():
        return QIcon(str(data_path))
    else:
        raise FileNotFoundError(icon_path)


def get_level_thumbnail(object_set, layout_address: "LevelAddress", enemy_address: "EnemyItemAddress"):
    """Return level thumbnail.

    It provides shared behavior used by the editor runtime. The lookup centralizes coordinate or identifier handling for callers.

    Parameters
    ----------
    object_set : Any
        Object set that controls tiles, graphics, or level object behavior.
    layout_address : 'LevelAddress'
        ROM address of the level or world map layout data.
    enemy_address : 'EnemyItemAddress'
        ROM enemy address.

    Returns
    -------
    Any
        The requested level thumbnail.
    """
    from foundry.game.level.LevelRef import LevelRef
    from foundry.gui.visualization.level.LevelView import LevelView

    level_ref = LevelRef()
    level_ref.load_level("", layout_address, enemy_address, object_set)

    view = LevelView(None, level_ref, Settings("mchlnix", "throwaway"), None)

    view.settings.setValue("level_view/block_transparency", object_set != DESERT_OBJECT_SET)

    view.zoom_out()
    view.zoom_out()

    return view.grab()


def pixmap_to_base64(pixmap: QPixmap) -> str:
    """Handle pixmap to base64.

    It provides shared behavior used by the editor runtime. The return value exposes the computed state expected by callers.

    Parameters
    ----------
    pixmap : QPixmap
        Pixmap used by the operation.

    Returns
    -------
    str
        Computed pixmap to base64.
    """
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    pixmap.save(buffer, "PNG", quality=100)
    image_data = bytes(buffer.data().toBase64()).decode()

    return image_data


def make_macro(undo_stack: QUndoStack, title: str, *commands: QUndoCommand):
    """Create macro.

    It provides shared behavior used by the editor runtime. The method delegates lower-level work while keeping the public workflow focused.

    Parameters
    ----------
    undo_stack : QUndoStack
        Undo stack that receives imported commands.
    title : str
        Window or menu title.
    *commands : QUndoCommand
        Commands used by the operation.
    """
    if not commands:
        return

    undo_stack.beginMacro(title)

    apply(undo_stack.push, commands)

    undo_stack.endMacro()
