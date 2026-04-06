import json
import urllib.error
import urllib.request
from http.client import IncompleteRead

from PySide6.QtWidgets import QMessageBox, QWidget

from foundry import get_current_version_name

SHORT_COMMIT_LENGTH = 8  # characters


def get_release_data(timeout: int = 10) -> bytes:
    owner = "mchlnix"
    repo = "SMB3-Foundry"

    api_call = f"https://api.github.com/repos/{owner}/{repo}/releases"

    try:
        request = urllib.request.urlopen(api_call, timeout=timeout)
    except urllib.error.URLError as ue:
        raise ValueError(f"Network error {ue}")

    try:
        return request.read()
    except IncompleteRead as icr:
        raise ValueError("Read corrupted data from the internet.") from icr


def get_latest_version_name_from_data(data: bytes) -> str:
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


def get_latest_nightly_hash(data: bytes) -> str:
    try:
        json_data = json.loads(data)

        for release_info in json_data:
            version_name = release_info["tag_name"].strip()

            if version_name == "nightly":
                return release_info["target_commitish"][:SHORT_COMMIT_LENGTH]
        else:
            # couldn't find nightly release
            return ""

    except (KeyError, IndexError, LookupError, json.JSONDecodeError):
        return ""


def is_nightly_new(new_nightly_hash: str):
    current_version = get_current_version_name()

    if not current_version.startswith("nightly-"):
        # current version is a stable release, nightly releases should always be newer than stable releases
        return True

    current_nightly_hash = current_version.removeprefix("nightly-")

    # we expect new hashes to be the same length or longer, but just in case make sure they are the same size
    if len(new_nightly_hash) < len(current_nightly_hash):
        current_nightly_hash = current_nightly_hash[: len(new_nightly_hash)]

    # there's always only one nightly release, and it's the most up to date, so if these don't match, there's a new one
    return not new_nightly_hash.startswith(current_nightly_hash)


def check_for_update(parent: QWidget) -> tuple[str, str]:
    try:
        data = get_release_data()

        latest_version_name = get_latest_version_name_from_data(data)
        latest_nightly_hash = get_latest_nightly_hash(data)

        return latest_version_name, latest_nightly_hash

    except ValueError as ve:
        QMessageBox.critical(parent, "Error while checking for updates", f"Error: {ve}")
        return "", ""
