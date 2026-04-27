"""Jump-list widget for level transition records.

This module provides the list view that mirrors the jump table attached to the
loaded level reference. The workflow is ``LevelRef`` jump data -> ``JumpList``
rows -> coarse add, edit, and remove signals that the main window turns into
dialogs and undoable commands.

See Also
--------
foundry.gui.ObjectList
    Companion list widget for objects and enemies in the same level.
foundry.gui.dialogs.JumpEditor
    Dialog that edits the jump records selected or created from this list.
"""

from PySide6.QtCore import Signal, SignalInstance
from PySide6.QtGui import QContextMenuEvent, QMouseEvent
from PySide6.QtWidgets import QListWidget, QMenu, QWidget

from foundry.game.level.LevelRef import LevelRef

ID_ADD_JUMP = 1
ID_DEL_JUMP = 2
ID_EDIT_JUMP = 3


class JumpList(QListWidget):
    """List and dispatch edits for level jump definitions.

    SMB3 levels can define jump zones for pipes and doors. The list mirrors the
    loaded level reference's jump table and emits coarse actions; the main window owns
    the dialogs and undo-stack changes.

    Parameters
    ----------
    parent : QWidget
        Parent Qt widget that owns this object.
    level_ref : LevelRef
        Reference to the loaded level.

    Attributes
    ----------
    _level_ref : LevelRef
        Reference that owns the loaded level-like model and jump list.
    add_jump : SignalInstance
        Signal emitted when the user requests a new jump.
    edit_jump : SignalInstance
        Signal emitted when the user requests editing the selected jump.
    remove_jump : SignalInstance
        Signal emitted when the user requests removing the selected jump.
    """

    add_jump: SignalInstance = Signal()
    edit_jump: SignalInstance = Signal()
    remove_jump: SignalInstance = Signal()

    def __init__(self, parent: QWidget, level_ref: LevelRef):
        """Create the jump list and wire it to the shared level reference.

        The widget listens for ``LevelRef.data_changed`` so the jump rows stay
        synchronized with header edits, undo commands, and level reloads.

        Parameters
        ----------
        parent : QWidget
            Parent Qt widget that owns this object.
        level_ref : LevelRef
            Reference to the level whose jump table is shown.
        """
        super(JumpList, self).__init__(parent)

        self._level_ref = level_ref

        self._level_ref.data_changed.connect(self.update)
        self.itemDoubleClicked.connect(lambda _: self.edit_jump.emit())

        self.setWhatsThis(
            "<b>Jump List</b><br/>"
            "Every level can designate another level to jump to, in case a pipe or a door is entered. This is done in "
            "the header, which can be edited with the Header Editor. While only one such level can be defined, where "
            "and how to enter that level can be defined multiple times with multiple jumps.<br/>"
            "A jump is valid for one screen, a 16-block wide/high section of the level, depending on if the level is "
            "vertical or not, and all objects within that section, capable of handling a jump, will jump to the same "
            "position in the same way. To see where these jump zones are, enable the Jump Zone option in the View menu."
            "<br/><br/>"
            "Tip: By having multiple jumps with different entry positions, you could make it look, like you are "
            "jumping to two different levels, when, in fact, you are jumping to two different sections of the same "
            "level."
        )

    def update(self):
        """Rebuild the list from the loaded level's jump table.

        ``LevelRef`` emits ``data_changed`` after jump edits, header changes,
        and level reloads, so the widget regenerates its rows from the live jump
        objects instead of trying to keep incremental UI state in sync.
        """
        self.clear()

        jumps = self._level_ref.jumps

        self.addItems([str(jump) for jump in jumps])

    def delete_selected_jump(self):
        """Request removal of the selected jump row."""
        index = self.currentRow()

        if index < 0:
            return

        self.remove_jump.emit()

    def focusOutEvent(self, event):
        """Clear row selection when focus leaves the list.

        Parameters
        ----------
        event : QFocusEvent
            Qt event delivered to the widget.
        """
        event.accept()
        self.clearSelection()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Delegate mouse release handling after ignoring the event locally.

        Ignoring the release first lets outer editor widgets keep their own
        selection and focus handling before Qt performs the list widget's
        default row-update behavior. That keeps jump-row selection changes from
        short-circuiting the broader editor focus choreography around the list.
        The release therefore still flows through Qt's list handling, but only
        after the surrounding level editor has had a chance to preserve its
        higher-level selection and focus state.

        Parameters
        ----------
        event : QMouseEvent
            Qt event delivered to the widget.

        Returns
        -------
        object
            Result returned by the base Qt handler, if any.
        """
        event.ignore()

        return super().mouseReleaseEvent(event)

    def contextMenuEvent(self, event: QContextMenuEvent):
        """Open add/edit/remove jump actions for the clicked row.

        Parameters
        ----------
        event : QContextMenuEvent
            Qt event delivered to the widget.
        """
        item = self.itemAt(event.pos())

        menu = QMenu()

        if item is None:
            add_action = menu.addAction("Add Jump")
            add_action.triggered.connect(self.add_jump.emit)

        else:
            edit_action = menu.addAction("Edit Jump")
            edit_action.triggered.connect(self.edit_jump.emit)

            remove_action = menu.addAction("Remove Jump")
            remove_action.triggered.connect(self.remove_jump.emit)

        menu.exec(event.globalPos())
