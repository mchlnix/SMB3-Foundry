"""Load and save standalone M3L level snapshots.

M3L files are Foundry's detached level persistence format. This module owns
the small file-dialog and byte-read/write boundary for that format: UI captions
are localized, while filesystem paths, serialized bytes, and level identities
remain stable data passed back to the editor model.
"""

from pathlib import Path

from PySide6.QtWidgets import QFileDialog, QMessageBox

from foundry import M3L_FILE_FILTER
from foundry.game.level.Level import Level
from foundry.gui.localization import tr

TR_CONTEXT = "M3L"


def load_m3l_filename(default_path=""):
    """Ask the user for an M3L file to import.

    The dialog caption is localized, but the returned filesystem path is not
    translated or normalized. The ``M3L_FILE_FILTER`` value is a file-dialog
    filter contract rather than catalog data. Callers own validation and import
    behavior after the user chooses a file.

    Parameters
    ----------
    default_path : str, optional
        Initial file or directory shown by the native file dialog.

    Returns
    -------
    str
        Selected path, or an empty string when the dialog is cancelled.
    """
    pathname, _ = QFileDialog.getOpenFileName(
        None,
        caption=tr(TR_CONTEXT, "open_m3l_file", "Open M3L file"),
        dir=default_path,
        filter=M3L_FILE_FILTER,
    )

    return pathname


def save_m3l_filename(default_path=""):
    """Ask the user where an M3L file should be saved.

    The dialog caption is localized at the UI boundary. The selected path
    and file filter remain stable filesystem/UI contract values and are
    returned unchanged to the caller.

    Parameters
    ----------
    default_path : str, optional
        Initial file or directory shown by the native file dialog.

    Returns
    -------
    str
        Selected path, or an empty string when the dialog is cancelled.
    """
    pathname, _ = QFileDialog.getSaveFileName(
        None,
        caption=tr(TR_CONTEXT, "save_m3l_as", "Save M3L as"),
        dir=default_path,
        filter=M3L_FILE_FILTER,
    )

    return pathname


def load_m3l(pathname: Path | str, level: Level):
    """Load M3L bytes into a level model.

    File-error text is localized for the warning dialog, but the path and M3L
    bytes remain filesystem/model data. The level name is derived from the file
    stem after a successful import and is not translated by this helper. The
    state flow is file bytes to ``Level.from_m3l`` to the active level model.

    Parameters
    ----------
    pathname : Path | str
        M3L file path to read.
    level : Level
        Level model that receives the parsed M3L data.
    """
    try:
        m3l_data = bytearray(Path(pathname).read_bytes())
    except IOError as exp:
        QMessageBox.warning(
            None,
            type(exp).__name__,
            tr(TR_CONTEXT, "cannot_open_file_pathname", "Cannot open file '{pathname}'.").format(pathname=pathname),
        )
        return

    level.from_m3l(m3l_data)

    level.name = Path(pathname).stem


def save_m3l(pathname: Path | str, m3l_bytes: bytearray):
    """Write M3L bytes to disk.

    Error messages are localized for the warning dialog. The output bytes and
    target path are persistence data and are not translated.

    Parameters
    ----------
    pathname : Path | str
        Destination M3L file path.
    m3l_bytes : bytearray
        Serialized M3L level data to write.
    """
    try:
        Path(pathname).write_bytes(m3l_bytes)
    except IOError as exp:
        QMessageBox.warning(
            None,
            type(exp).__name__,
            tr(TR_CONTEXT, "couldn_t_save_level_to_pathname", "Couldn't save level to '{pathname}'.").format(
                pathname=pathname
            ),
        )
