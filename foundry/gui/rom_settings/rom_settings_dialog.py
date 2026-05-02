"""ROM-scoped settings dialogs and maintenance entry points.

This module hosts the dialog surface for settings and tools that affect the
whole loaded ROM rather than one level. The workflow is ROM-scoped settings
surface -> mixin-owned state and commands -> main-window refresh, with the
shared dialog shell carrying the active level reference through that flow.

See Also
--------
foundry.gui.rom_settings.managed_levels_mixin
    Adds managed-level-position controls to this dialog.
foundry.game.level.LevelRef
    Carries the active editor session into ROM-scoped tools.
"""

from PySide6.QtCore import Signal, SignalInstance
from PySide6.QtGui import QUndoStack

from foundry.game.level.LevelRef import LevelRef
from foundry.gui.dialogs.CustomDialog import CustomDialog
from foundry.gui.localization import tr
from foundry.gui.rom_settings.managed_levels_mixin import ManagedLevelsMixin


class RomSettingsDialog(ManagedLevelsMixin, CustomDialog):
    """Display ROM-wide editor settings and maintenance tools.

    The dialog is currently centered on managed level positions, but it acts as
    the shared container for ROM-scoped settings that are broader than any
    single level. It provides the level reference and refresh signal that the
    mixins use to coordinate with the main window.

    Parameters
    ----------
    parent : object
        Parent Qt widget that owns this object.
    level_ref : LevelRef
        Reference to the loaded level.

    Attributes
    ----------
    level_ref : LevelRef
        Reference to the loaded level.
    needs_gui_update : SignalInstance
        Signal emitted when ROM-setting changes require the main UI to refresh.

    Notes
    -----
    The dialog's workflow is ROM-scoped settings UI -> mixin-owned mutations ->
    main-window refresh. It is intentionally broader than per-level settings,
    even though it still needs a level reference for coordination.
    """

    needs_gui_update: SignalInstance = Signal()

    def __init__(self, parent, level_ref: LevelRef):
        """Build the ROM settings dialog around the active editor session.

        The dialog hands the loaded level reference and a shared refresh signal
        to its mixins so ROM-scoped tools can coordinate with the active editor state
        without becoming direct main-window dependencies or duplicating open
        session state.

        Parameters
        ----------
        parent : QWidget
            Parent Qt widget that owns this object.
        level_ref : LevelRef
            Reference to the level loaded in the editor.
        """
        self.level_ref = level_ref

        super(RomSettingsDialog, self).__init__(parent)

        self.retranslate_ui()

        self.update()

    def retranslate_ui(self) -> None:
        """Refresh the ROM-settings title without changing ROM edit state.

        The dialog shell text is rebuilt from the active catalog. The level
        reference, staged ROM-setting widgets, and shared undo-stack target stay
        stable so localization only changes the visible title.
        """
        self.setWindowTitle(tr("RomSettingsDialog", "rom_settings", "ROM Settings"))

    @property
    def undo_stack(self) -> QUndoStack:
        """Main-window undo stack used by ROM settings actions.

        ROM-scoped tools still participate in the shared undo history rather
        than keeping their own stack, which keeps ROM-wide edits consistent
        with the rest of the editor workflow.

        Returns
        -------
        QUndoStack
            Shared undo stack owned by the main window.
        """
        return self.parent().window().findChild(QUndoStack, "undo_stack")

    def update(self):
        """Refresh mixin-owned controls for the active ROM state.

        The dialog delegates most of its surface area to mixins, so an update
        call primarily asks those mixins to rebuild their derived UI from the
        latest ROM state and open level reference.
        """
        super(RomSettingsDialog, self).update()

    def closeEvent(self, event):
        """Close the dialog after delegating to mixins and the base class.

        Parameters
        ----------
        event : QCloseEvent
            Qt event delivered to the widget.
        """
        super(RomSettingsDialog, self).closeEvent(event)
