import json
import urllib.request
import urllib.error
from pathlib import Path
from typing import Union

from PySide2.QtCore import QUrl
from PySide2.QtGui import QDesktopServices, QIcon

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


def open_url(url: Union[str, QUrl]):
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

    data = request.read()

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


def icon(icon_name: str):
    icon_path = icon_dir / icon_name
    data_path = data_dir / icon_name

    if icon_path.exists():
        return QIcon(str(icon_path))
    elif data_path.exists():
        return QIcon(str(data_path))
    else:
        raise FileNotFoundError(icon_path)
