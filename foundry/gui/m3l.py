from pathlib import Path

from PySide6.QtWidgets import QFileDialog, QMessageBox

from foundry import M3L_FILE_FILTER
from foundry.game.level.Level import Level


def load_m3l_filename(default_path=""):
    """Load m3l filename.

    It connects Qt UI behavior with the editor model and command workflow. The data boundary keeps ROM/file operations explicit for callers.

    Parameters
    ----------
    default_path : Any, optional
        Path to the default file or directory.

    Returns
    -------
    Any
        Loaded or parsed data.
    """
    pathname, _ = QFileDialog.getOpenFileName(None, caption="Open M3L file", dir=default_path, filter=M3L_FILE_FILTER)

    return pathname


def save_m3l_filename(default_path=""):
    """Save m3l filename.

    It connects Qt UI behavior with the editor model and command workflow. The data boundary keeps ROM/file operations explicit for callers.

    Parameters
    ----------
    default_path : Any, optional
        Path to the default file or directory.

    Returns
    -------
    Any
        Computed save m3l filename.
    """
    pathname, _ = QFileDialog.getSaveFileName(None, caption="Save M3L as", dir=default_path, filter=M3L_FILE_FILTER)

    return pathname


def load_m3l(pathname: Path | str, level: Level):
    """Load m3l.

    It connects Qt UI behavior with the editor model and command workflow. The data boundary keeps ROM/file operations explicit for callers.

    Parameters
    ----------
    pathname : Path | str
        Filesystem path used by the operation.
    level : Level
        Level model or level reference used by the operation.
    """
    try:
        m3l_data = bytearray(Path(pathname).read_bytes())
    except IOError as exp:
        QMessageBox.warning(None, type(exp).__name__, f"Cannot open file '{pathname}'.")
        return

    level.from_m3l(m3l_data)

    level.name = Path(pathname).stem


def save_m3l(pathname: Path | str, m3l_bytes: bytearray):
    """Save m3l.

    It connects Qt UI behavior with the editor model and command workflow. The data boundary keeps ROM/file operations explicit for callers.

    Parameters
    ----------
    pathname : Path | str
        Filesystem path used by the operation.
    m3l_bytes : bytearray
        Bytes containing the m3l data.
    """
    try:
        Path(pathname).write_bytes(m3l_bytes)
    except IOError as exp:
        QMessageBox.warning(None, type(exp).__name__, f"Couldn't save level to '{pathname}'.")
