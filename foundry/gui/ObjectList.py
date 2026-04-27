"""Object-list widget for level object and enemy ordering.

This module provides the list view that mirrors Foundry's editable object
stream for the loaded level. The workflow is ``LevelRef`` object data ->
``ObjectList`` rows -> shared selection and context-menu actions that stay in
sync with the level canvas and other editor surfaces.

See Also
--------
foundry.gui.ContextMenu
    Provides the shared level context menu opened from right-click actions.
foundry.gui.JumpList
    Companion list widget for jump records omitted from the object stream.
"""

from PySide6.QtCore import QModelIndex, Signal, SignalInstance
from PySide6.QtGui import QMouseEvent, Qt
from PySide6.QtWidgets import QListWidget, QSizePolicy, QWidget

from foundry.game.level.LevelRef import LevelRef
from foundry.gui.ContextMenu import LevelContextMenu


class ObjectList(QListWidget):
    """List editable level objects in ROM draw order.

    The widget reflects Foundry's editing view of SMB3 level contents rather
    than just acting as a generic list box. It shows the combined level-object
    and enemy/item stream in ROM order, which is also the order that affects
    draw layering in the editor and in-game. Jumps are omitted because Foundry
    edits them through a dedicated jump list. Right-click handling first stages
    selection on the row under the cursor, then opens the shared level context
    menu so list actions apply to the item the user actually targeted.

    Parameters
    ----------
    parent : QWidget
        Parent Qt widget that owns this object.
    level_ref : LevelRef
        Reference to the edited level.
    context_menu : LevelContextMenu
        Context menu populated or displayed by the widget.

    Attributes
    ----------
    context_menu : LevelContextMenu
        Context menu displayed for list objects.
    level_ref : LevelRef
        Reference that owns the edited level and selection.
    selection_changed : SignalInstance
        Signal emitted with the selected objects after list selection changes.
    """

    selection_changed: SignalInstance = Signal(list)

    def __init__(self, parent: QWidget, level_ref: LevelRef, context_menu: LevelContextMenu):
        """Create the object list and bind it to level selection state.

        The list subscribes to ``LevelRef.data_changed`` so reorder, add,
        delete, and undo flows rebuild the visible rows from the live level
        model. It also keeps the shared context menu attached to the same row
        selection semantics used by the canvas, which lets list-driven actions
        operate on the same selected object set as viewport-driven actions.

        Parameters
        ----------
        parent : QWidget
            Parent Qt widget that owns this object.
        level_ref : LevelRef
            Reference to the edited level.
        context_menu : LevelContextMenu
            Context menu populated or displayed by the widget.
        """
        super(ObjectList, self).__init__(parent=parent)

        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.setSelectionMode(self.SelectionMode.ExtendedSelection)

        self.level_ref: LevelRef = level_ref
        self.level_ref.data_changed.connect(self.update_content)

        self.context_menu = context_menu

        self.itemSelectionChanged.connect(self.on_selection_changed)

        self.setWhatsThis(
            "<b>Object List</b><br/>"
            "This lists all the objects and enemies/items in the level. They appear in the order, "
            "that they are stored in the ROM as, which also decides which objects get drawn "
            "before/behind which.<br/>"
            "Enemies/items are always listed last, since they are also stored separately from the level "
            "objects.<br/><br/>"
            "Note: While Jumps are technically level objects, they are omitted here, since they are "
            "listed in a separate list below."
        )

    def mousePressEvent(self, event: QMouseEvent):
        """Start right-click context selection or delegate normal presses.

        Right-button presses are intercepted so the row under the cursor can
        become the active editor selection before the shared context menu is
        opened. All other mouse presses continue through Qt's default list
        handling, which keeps ordinary list selection and drag semantics owned
        by Qt while right-clicks stay aligned with Foundry's shared
        object-selection workflow.

        Parameters
        ----------
        event : QMouseEvent
            Qt event delivered to the widget.

        Returns
        -------
        object
            Result returned by Qt for non-right-click handling.
        """
        if event.button() == Qt.MouseButton.RightButton:
            self.on_right_down(event)

            return None
        else:
            event.ignore()
            return super(ObjectList, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Open the context menu on right release or delegate normal releases.

        The release phase completes the two-step right-click workflow started
        in ``mousePressEvent``: first stage the correct row selection, then
        open the level context menu against that staged target. Non-right
        releases continue through the normal Qt selection path.

        Parameters
        ----------
        event : QMouseEvent
            Qt event delivered to the widget.

        Returns
        -------
        object
            Result returned by Qt for non-right-click handling.
        """
        if event.button() == Qt.MouseButton.RightButton:
            self.on_right_up(event)

            return None
        else:
            event.ignore()
            return super(ObjectList, self).mouseReleaseEvent(event)

    def on_right_down(self, event: QMouseEvent):
        """Select the object under the cursor before a context-menu action.

        Parameters
        ----------
        event : QMouseEvent
            Qt event delivered to the widget.
        """
        item_under_mouse = self.itemAt(event.position().toPoint())

        if item_under_mouse is None:
            event.ignore()
            return

        if not item_under_mouse.isSelected():
            self.clearSelection()

            index = self.indexFromItem(item_under_mouse)

            selected_object = self.level_ref.level.get_all_objects()[index.row()]

            self.level_ref.selected_objects = [selected_object]

    def on_right_up(self, event):
        """Show the level context menu for the object under the cursor.

        Parameters
        ----------
        event : QMouseEvent
            Qt event delivered to the widget.
        """
        item_under_mouse = self.itemAt(event.position().toPoint())

        if item_under_mouse is None:
            event.ignore()
            return

        index: QModelIndex = self.indexFromItem(item_under_mouse)

        level_object = self.level_ref.level.objects[index.row()]

        self.context_menu.as_list_menu(level_object).popup(event.globalPos())

    def update_content(self):
        """Synchronize list rows with the editable object stream.

        Signals are blocked while rows are inserted, renamed, removed, and
        reselected so refreshes driven by level mutations do not echo back into
        ``LevelRef.selected_objects`` as if the user had changed the selection.
        """
        level_objects = self.level_ref.get_all_objects()

        self.blockSignals(True)

        for index, level_object in enumerate(level_objects):
            # insert potentially new items
            if (item := self.item(index)) is None:
                self.insertItem(index, level_object.name)
                item = self.item(index)

            # update level objects name and associated data, if it has changed (moved, deleted, added)
            if level_object != item.data(Qt.ItemDataRole.UserRole):
                item.setText(level_object.name)
                item.setData(Qt.ItemDataRole.UserRole, level_object)

            item.setSelected(level_object.selected)

        # in case of object deletion, remove all unnecessary objects
        while self.count() > len(level_objects):
            self.takeItem(self.count() - 1)

        self.blockSignals(False)

        if self.selectedIndexes():
            self.scrollTo(self.selectedIndexes()[-1])

    def selected_objects(self):
        """Objects currently selected through the list widget.

        The method is the bridge from Qt row selection back into the level
        model, returning the underlying object instances that other editor
        surfaces expect when synchronizing selection state.

        Returns
        -------
        list
            Level objects or enemies attached to the selected rows.
        """
        return [self.item(index.row()).data(Qt.ItemDataRole.UserRole) for index in self.selectedIndexes()]

    def on_selection_changed(self):
        # only called by ourselves
        """Propagate user selection changes back to ``LevelRef``.

        The equality check prevents refresh-driven selection updates from
        emitting duplicate selection changes into the rest of the editor.
        """
        selected_objects = self.selected_objects()

        selection_not_changed = selected_objects == self.level_ref.selected_objects

        if selection_not_changed:
            return
        else:
            self.level_ref.selected_objects = selected_objects
            self.selection_changed.emit(selected_objects)
