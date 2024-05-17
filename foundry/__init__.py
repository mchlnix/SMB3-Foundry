import json
import urllib.error
import urllib.request
from functools import lru_cache
from http.client import IncompleteRead
from pathlib import Path
from typing import TYPE_CHECKING, cast

from PySide6.QtCore import QBuffer, QIODevice, QUrl
from PySide6.QtGui import QDesktopServices, QIcon, QPixmap, Qt, QUndoCommand, QUndoStack
from PySide6.QtWidgets import QApplication, QMessageBox, QWidget

from foundry.gui.settings import Settings
from smb3parse.objects.object_set import DESERT_OBJECT_SET
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


NO_PARENT = cast(QWidget, None)


def ctrl_is_pressed():
    return bool(QApplication.keyboardModifiers() & Qt.ControlModifier)


def shift_is_pressed():
    return bool(QApplication.keyboardModifiers() & Qt.ShiftModifier)


def open_url(url: str | QUrl):
    QDesktopServices.openUrl(QUrl(url))


def get_current_version_name() -> str:
    version_file = root_dir / "VERSION"

    if not version_file.exists():
        raise LookupError("Version file not found.")

    return version_file.read_text().strip()


def get_latest_version_name(timeout: int = 10) -> str:
    owner = "mchlnix"
    repo = "SMB3-Foundry"

    api_call = f"https://api.github.com/repos/{owner}/{repo}/releases"

    try:
        request = urllib.request.urlopen(api_call, timeout=timeout)
    except urllib.error.URLError as ue:
        raise ValueError(f"Network error {ue}")

    try:
        data = request.read()
    except IncompleteRead as icr:
        raise ValueError("Read corrupted data from the internet.") from icr

    try:
        json_data = json.loads(data)

        for release_info in json_data:
            version_name = release_info["tag_name"].strip()

            if version_name != "nightly":
                return version_name
        else:
            raise LookupError("Couldn't find a non-nightly release.")

    except (KeyError, IndexError, LookupError, json.JSONDecodeError):
        raise ValueError("Parsing the received information failed.")


def check_for_update(parent: QWidget) -> str:
    try:
        return get_latest_version_name()
    except ValueError as ve:
        QMessageBox.critical(parent, "Error while checking for updates", f"Error: {ve}")
        return ""


@lru_cache(256)
def icon(icon_name: str):
    icon_path = icon_dir / icon_name
    data_path = data_dir / icon_name

    if icon_path.exists():
        return QIcon(str(icon_path))
    elif data_path.exists():
        return QIcon(str(data_path))
    else:
        raise FileNotFoundError(icon_path)


def get_level_thumbnail(object_set, layout_address: "LevelAddress", enemy_address: "EnemyItemAddress"):
    from foundry.game.level.LevelRef import LevelRef
    from foundry.gui.visualization.level.LevelView import LevelView

    level_ref = LevelRef()
    level_ref.load_level("", layout_address, enemy_address, object_set)

    view = LevelView(None, level_ref, Settings("mchlnix", "throwaway"), None)

    view.settings.setValue("level view/block_transparency", object_set != DESERT_OBJECT_SET)

    view.zoom_out()
    view.zoom_out()

    return view.grab()


def pixmap_to_base64(pixmap: QPixmap) -> str:
    buffer = QBuffer()
    buffer.open(QIODevice.WriteOnly)
    pixmap.save(buffer, "PNG", quality=100)
    image_data = bytes(buffer.data().toBase64()).decode()

    return image_data


def make_macro(undo_stack: QUndoStack, title: str, *commands: QUndoCommand):
    if not commands:
        return

    undo_stack.beginMacro(title)

    apply(undo_stack.push, commands)

    undo_stack.endMacro()
