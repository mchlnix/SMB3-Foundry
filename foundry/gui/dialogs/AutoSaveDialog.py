"""Prompt the user to choose how crash-recovery autosaves should be handled.

This module contains the small recovery dialog shown when Foundry detects an
autosaved ROM from the previous session. It is part of the startup recovery
workflow rather than normal editing, and it exists so the application can turn
recovered state into one explicit user choice before loading or discarding the
autosave.
"""

from PySide6.QtWidgets import QMessageBox

from foundry.gui.localization import tr

TR_KEY_CONTEXT = "foundry.startup"


def _startup_text(key: str, fallback: str) -> str:
    """Resolve autosave recovery text from stable startup catalog keys.

    Parameters
    ----------
    key : str
        ``foundry.startup`` catalog key for the recovery dialog.
    fallback : str
        English text used when the selected locale has no value.

    Returns
    -------
    str
        Localized Qt display text. Autosave file paths and recovery choices
        remain stable runtime state outside the translation catalog.
    """
    return tr(TR_KEY_CONTEXT, key, fallback)


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

        self.setIcon(QMessageBox.Icon.Warning)

        self.discard_rom_button = self.addButton("", QMessageBox.ButtonRole.DestructiveRole)
        self.use_auto_save_button = self.addButton("", QMessageBox.ButtonRole.AcceptRole)
        self.setDefaultButton(self.use_auto_save_button)
        self.retranslate_ui()

    def retranslate_ui(self) -> None:
        """Refresh the recovery prompt from the active translation catalog.

        Live language switching updates only display text: the window title,
        prompt body, and the two existing button labels. The button objects are
        deliberately preserved because startup recovery code compares the
        clicked button with ``discard_rom_button`` and ``use_auto_save_button``
        to decide whether to discard or load the recovered autosave.
        """
        self.setWindowTitle(_startup_text("autosave.restore.title", "Rom was recovered"))
        self.setText(
            _startup_text(
                "autosave.restore.prompt",
                "We found an auto saved ROM from the last session. Do you want to open it?",
            )
        )
        self.discard_rom_button.setText(_startup_text("autosave.restore.discard", "Discard Auto Save"))
        self.use_auto_save_button.setText(_startup_text("autosave.restore.load", "Load Auto Save"))
