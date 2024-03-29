from pathlib import Path

from PySide6.QtWidgets import QFileDialog, QMessageBox

from foundry import M3L_FILE_FILTER
from foundry.game.level.Level import Level


def load_m3l_filename(default_path=""):
    pathname, _ = QFileDialog.getOpenFileName(None, caption="Open M3L file", dir=default_path, filter=M3L_FILE_FILTER)

    return pathname


def save_m3l_filename(default_path=""):
    pathname, _ = QFileDialog.getSaveFileName(None, caption="Save M3L as", dir=default_path, filter=M3L_FILE_FILTER)

    return pathname


def load_m3l(pathname: Path | str, level: Level):
    try:
        m3l_data = bytearray(Path(pathname).read_bytes())
    except IOError as exp:
        QMessageBox.warning(None, type(exp).__name__, f"Cannot open file '{pathname}'.")
        return

    level.from_m3l(m3l_data)

    level.name = Path(pathname).stem


def save_m3l(pathname: Path | str, m3l_bytes: bytearray):
    try:
        Path(pathname).write_bytes(m3l_bytes)
    except IOError as exp:
        QMessageBox.warning(None, type(exp).__name__, f"Couldn't save level to '{pathname}'.")
