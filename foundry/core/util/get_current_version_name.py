from foundry import root_dir


def get_current_version_name() -> str:
    """Get version name"""
    version_file = root_dir / "VERSION"

    if not version_file.exists():
        raise LookupError("Version file not found.")

    return version_file.read_text().strip()