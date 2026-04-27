"""Prompt the user to choose how crash-recovery autosaves should be handled.

This module contains the small recovery dialog shown when Foundry detects an
autosaved ROM from the previous session. It is part of the startup recovery
workflow rather than normal editing, and it exists so the application can turn
recovered state into one explicit user choice before loading or discarding the
autosave.
"""

from PySide6.QtWidgets import QMessageBox


class AutoSaveDialog(QMessageBox):
    """Ask whether a recovered autosave ROM should be loaded.

    Foundry shows this prompt after crash recovery discovers an autosaved ROM
    from the previous session. The dialog is intentionally tiny: it presents
    the recovery choice and exposes the two action buttons for callers that
    need to inspect which path the user chose.

    Attributes
    ----------
    discard_rom_button : QMessageBox.StandardButton | object
        Button that discards the recovered autosave.
    use_auto_save_button : QMessageBox.StandardButton | object
        Button that opens the recovered autosave.

    Notes
    -----
    The destructive option is deliberately labeled in terms of the autosave
    file, not the user's original ROM, to make the recovery decision clearer.
    """

    def __init__(self):
        """Build the autosave recovery prompt.

        The constructor wires the recovery message, warning styling, and the
        two explicit branch choices that the startup workflow later checks to
        decide whether recovered ROM state is loaded or discarded.
        """
        super(AutoSaveDialog, self).__init__()

        self.setWindowTitle("Rom was recovered")
        self.setText("We found an auto saved ROM from the last session. Do you want to open it?")
        self.setIcon(QMessageBox.Icon.Warning)

        self.discard_rom_button = self.addButton("Discard Auto Save", QMessageBox.ButtonRole.DestructiveRole)
        self.use_auto_save_button = self.addButton("Load Auto Save", QMessageBox.ButtonRole.AcceptRole)
        self.setDefaultButton(self.use_auto_save_button)
