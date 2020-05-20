import json
import urllib.request
import urllib.error
from pathlib import Path

from PySide2.QtCore import QUrl
from PySide2.QtGui import QDesktopServices

root_dir = Path(__file__).parent.parent

data_dir = root_dir.joinpath("data")

icon_dir = data_dir.joinpath("icons")

releases_link = "https://github.com/mchlnix/SMB3-Foundry/releases"
feature_video_link = "https://www.youtube.com/watch?v=7_22cAffMmE"
discord_link = "https://discord.gg/pm87gm7"


def open_url(url: str):
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
        return json.loads(data)[0]["tag_name"].strip()
    except (KeyError, IndexError, json.JSONDecodeError):
        raise ValueError("Parsing the received information failed.")
