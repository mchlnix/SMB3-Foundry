"""Composite dialog for SMB3 level-setting mixins.

This module assembles the specialized level-settings mixins into the dialog
that edits miscellaneous per-level settings outside the main header editor.
The workflow is editor ``LevelRef`` -> mixin-owned staged widgets -> shared
close handling that converts staged changes back into undoable commands for
the main editor.

See Also
--------
foundry.gui.level_settings.settings_mixin
    Provides the shared level-reference and close-chain behavior used by the
    specialized settings mixins.
foundry.gui.dialogs.LevelHeaderEditor
    Edits the encoded level-header bytes that complement the settings exposed
    here.
"""

from PySide6.QtGui import QUndoStack

from foundry.game.level.LevelRef import LevelRef
from foundry.gui.dialogs.CustomDialog import CustomDialog
from foundry.gui.level_settings.auto_scroll_mixin import AutoScrollMixin
from foundry.gui.level_settings.boom_boom_mixin import BoomBoomMixin
from foundry.gui.level_settings.chest_exit_mixin import ChestExitMixin
from foundry.gui.level_settings.pipe_pair_mixin import PipePairMixin
from foundry.gui.level_settings.white_mushroom_mixin import WhiteMushroomHouseMixin


class LevelSettingsDialog(
    PipePairMixin, WhiteMushroomHouseMixin, ChestExitMixin, BoomBoomMixin, AutoScrollMixin, CustomDialog
):
    """Display the miscellaneous level-settings editor.

    The dialog is composed from mixins that each stage edits to special SMB3
    enemy/item records or header-adjacent settings. Most controls mutate the
    in-memory level while the dialog is open, then close handlers translate the
    difference from the original state into undoable commands.

    Parameters
    ----------
    parent : object
        Parent window that owns the level view and undo stack.
    level_ref : LevelRef
        Reference to the loaded level.

    Attributes
    ----------
    level_ref : LevelRef
        Reference to the loaded level.

    Notes
    -----
    This dialog is effectively a composition root for several specialized
    settings mixins. Each mixin owns one narrow concern, while the dialog
    provides the shared level reference and undo-stack access they all need.
    The workflow is staged edits in each mixin -> cooperative close handling ->
    undoable commands pushed back to the main editor.
    """

    def __init__(self, parent, level_ref: LevelRef):
        """Create the level-settings dialog for a level reference.

        The ``level_ref`` is stored before cooperative mixin initialization so
        each mixin can build controls from the level loaded in the editor and
        snapshot the bytes or special enemy records it needs for close-time
        undo reconstruction. The dialog itself is mostly a coordinator that
        binds those specialized editors to one shared level reference and undo
        stack for one level-settings session. That setup is what allows mixins
        to mutate temporary level state while the dialog is open and then let
        cooperative close handlers translate the net result back into undo
        commands.

        Parameters
        ----------
        parent : object
            Parent window that owns the level view and undo stack.
        level_ref : LevelRef
            Reference to the level being edited.
        """
        self.level_ref = level_ref

        super(LevelSettingsDialog, self).__init__(parent)

        self.setWindowTitle("Other Level Settings")

        self.update()

    @property
    def undo_stack(self) -> QUndoStack:
        """Expose the shared editor undo stack for every settings mixin.

        Mixins push their close-time commands here so setting changes behave
        like other editor actions and join the same save, autosave, and dirty
        state lifecycle as viewport-driven edits.

        Returns
        -------
        QUndoStack
            Undo stack named ``undo_stack`` in the owning window.
        """
        return self.parent().window().findChild(QUndoStack, "undo_stack")

    def update(self):
        """Refresh every mixin in the cooperative update chain.

        Individual mixins synchronize controls from the loaded level state and
        refresh any temporary preview state they own while the dialog is open.
        """
        super(LevelSettingsDialog, self).update()

    def closeEvent(self, event):
        """Let each settings mixin commit staged changes on close.

        The cooperative close chain converts temporary model mutations into
        undoable commands before the dialog is destroyed.

        Parameters
        ----------
        event : object
            Qt event delivered to the widget.
        """
        super(LevelSettingsDialog, self).closeEvent(event)
