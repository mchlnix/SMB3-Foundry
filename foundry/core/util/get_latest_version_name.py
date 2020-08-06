import json
import urllib.error
import urllib.request


def get_latest_version_name(timeout: int = 10) -> str:
    """Get github's last version name"""
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