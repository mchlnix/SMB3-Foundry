#!/usr/bin/env python3
"""Start the Scribe world-map editor from source or packaged builds.

This entrypoint mirrors the main Foundry startup boundary for the Scribe tool:
it normalizes PyInstaller's data directory, installs the persisted Scribe UI
language before creating widgets, forwards the optional ROM path to the Scribe
main window, and routes fatal startup errors through the shared crash dialog.
World-map parsing, ROM state, and editor command behavior remain owned by
``ScribeMainWindow`` after this process-level setup completes.
"""

import logging
import os
import sys
import traceback

from PySide6.QtWidgets import QApplication

from foundry import is_pyinstalled
from foundry.gui.dialogs.crash_dialog import popup_crash_dialog
from foundry.gui.localization import install_language_from_settings
from foundry.gui.settings import Settings
from scribe.gui.main_window import ScribeMainWindow

logger = logging.getLogger(__name__)

# change into the tmp directory pyinstaller uses for the data
if is_pyinstalled():
    logger.info(f"Changing current dir to {getattr(sys, '_MEIPASS')}")
    os.chdir(getattr(sys, "_MEIPASS"))

app = None


def main(path_to_rom):
    """Create the Qt app and open Scribe's main window.

    Parameters
    ----------
    path_to_rom : str
        Optional ROM path supplied on the command line. The entrypoint forwards
        the value unchanged so Scribe's main window owns validation, ROM
        loading, and any user-facing error handling.
    """
    global app

    app = QApplication()
    install_language_from_settings(app, Settings("mchlnix", "smb3scribe"))

    window = ScribeMainWindow(path_to_rom)  # noqa
    app.exec()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = ""

    try:
        main(path)
    except Exception:
        if app is None:
            app = QApplication()
            install_language_from_settings(app, Settings("mchlnix", "smb3scribe"))

        popup_crash_dialog(traceback.format_exc())

        raise
