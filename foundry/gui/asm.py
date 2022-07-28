from os import PathLike
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtWidgets import QFileDialog, QMessageBox

from foundry import ASM_FILE_FILTER
from foundry.gui.ObjectSetSelector import ObjectSetSelector

if TYPE_CHECKING:
    from foundry.game.level.Level import Level


def asm_to_bytes(asm: str) -> bytearray:
    ret = bytearray()

    for line in asm.split("\n"):
        before_comment, *_after_comment = line.split(";")

        if not (stripped_line := before_comment.strip()):
            continue

        if ".byte" not in stripped_line:
            continue

        bytes_in_line = [int(byte, 16) for byte in stripped_line.replace(", ", "").split("$")[1:]]

        ret.extend(bytes_in_line)

    ret.append(0xFF)

    return ret


def load_asm_filename(what: str, default_path=""):
    pathname, _ = QFileDialog.getOpenFileName(
        None, caption=f"Open {what} file", dir=default_path, filter=ASM_FILE_FILTER
    )

    return pathname


def save_asm_filename(what: str, default_path=""):
    pathname, _ = QFileDialog.getSaveFileName(
        None,
        caption=f"Save {what} as",
        dir=default_path,
        filter=ASM_FILE_FILTER,
    )

    return pathname


def load_asm_level(pathname: PathLike, level: "Level"):
    try:
        with open(pathname, "r") as asm_file:
            asm_level_data = asm_file.read()
    except IOError as exp:
        QMessageBox.warning(None, type(exp).__name__, f"Cannot open file '{pathname}'.")
        return

    object_set = ObjectSetSelector.get_object_set()

    if object_set == -1:
        # was cancelled
        return

    level.from_asm(object_set, asm_to_bytes(asm_level_data))

    level.name = Path(pathname).stem


def load_asm_enemy(pathname: PathLike, level: "Level"):
    try:
        with open(pathname, "r") as asm_file:
            asm_enemy_data = asm_file.read()
    except IOError as exp:
        QMessageBox.warning(None, type(exp).__name__, f"Cannot open file '{pathname}'.")
        return

    _, (__, current_enemy_bytes) = level.to_bytes()

    level._load_enemies(current_enemy_bytes[:-1] + asm_to_bytes(asm_enemy_data)[1:])

    level.data_changed.emit()


def save_asm(what: str, pathname: PathLike, asm_data: str):
    try:
        with open(pathname, "w") as asm_file:
            asm_file.write(asm_data)
    except IOError as exp:
        QMessageBox.warning(None, type(exp).__name__, f"Couldn't save {what} to '{pathname}'.")
