"""Render and edit world-map level pointers inside Scribe's tool window.

This module provides :class:`LevelPointerList`, a table widget that mirrors the
level-pointer rows from the active world model, routes in-cell edits through the
undo stack, and refreshes the list after drag-reordering or command-driven
updates. In the editor workflow, it is the tool-window surface where pointer
metadata leaves delegate widgets, becomes undoable Scribe commands, and then
returns to the world model as repaintable state. Maintainers tracing pointer
edits usually want to read next through ``scribe.gui.commands`` for the undo
commands and ``scribe.gui.tool_window.table_widget`` for the shared table
behaviors.
"""

import typing

from PySide6.QtGui import QDropEvent
from PySide6.QtWidgets import QComboBox, QTableWidgetItem

from foundry.game.level.LevelRef import LevelRef
from foundry.gui.widgets.Spinner import Spinner
from scribe.gui.commands import (
    ChangeLevelPointerIndex,
    SetEnemyAddress,
    SetLevelAddress,
    SetObjectSet,
)
from scribe.gui.tool_window.table_widget import (
    DialogDelegate,
    DropdownDelegate,
    SpinBoxDelegate,
    TableWidget,
)
from smb3parse.constants import OBJECT_SET_NAMES
from smb3parse.levels import FIRST_VALID_ROW


class LevelPointerList(TableWidget):
    """Expose world-map level pointers as an editable table surface.

    The widget adapts ``self.world.level_pointers`` into four editable columns:
    object set, level address, enemy address, and a read-only map position
    summary. Cell edits are converted into Scribe command objects so pointer
    mutations stay undoable and synchronized with the rest of the world-editing
    workflow.

    Parameters
    ----------
    parent
        Parent Qt widget that owns the table inside the tool window.
    level_ref : LevelRef
        Level reference whose world data populates the table and receives
        pointer updates.

    Attributes
    ----------
    world
        World model inherited from :class:`TableWidget` that supplies the level
        pointers and emits change notifications after command application.

    See Also
    --------
    scribe.gui.commands.ChangeLevelPointerIndex
        Undo command used when rows are drag-reordered.
    scribe.gui.tool_window.table_widget.TableWidget
        Shared world-aware table base that provides the undo stack and icon
        helpers used by this widget.
    """

    def __init__(self, parent, level_ref: LevelRef):
        """Configure the table columns, delegates, and edit callbacks.

        The constructor binds the table to the shared world-aware base class,
        installs column delegates that match each editable pointer field, and
        connects the Qt ``cellChanged`` signal to
        :meth:`_save_level_pointer`. That signal path is the bridge from a
        local widget edit to an undoable Scribe command, so the initial
        population is deferred to :meth:`update_content` after the delegates are
        ready.

        Parameters
        ----------
        parent
            Parent Qt widget that hosts the pointer list.
        level_ref : LevelRef
            Level reference whose world model provides the pointer rows shown in
            the table.
        """

        super(LevelPointerList, self).__init__(parent, level_ref)

        self.cellChanged.connect(self._save_level_pointer)

        self.set_headers(["Object Set", "Level Offset", "Enemy/Item Offset", "Map Position"])

        self.setItemDelegateForColumn(0, DropdownDelegate(self, OBJECT_SET_NAMES))
        self.setItemDelegateForColumn(1, SpinBoxDelegate(self))
        self.setItemDelegateForColumn(2, SpinBoxDelegate(self))
        self.setItemDelegateForColumn(
            3,
            DialogDelegate(
                self,
                "No can do",
                "You can move level pointers by dragging them around in the WorldView. "
                "Make sure they are shown in the View Menu.",
            ),
        )

        self.update_content()

    def dropEvent(self, event: QDropEvent) -> None:
        """Reorder level pointers through the undo stack after a drag drop.

        Parameters
        ----------
        event : QDropEvent
            Qt drop event whose source and target rows identify the moved level
            pointer.

        Notes
        -----
        The widget does not reorder the underlying model directly. It pushes a
        :class:`scribe.gui.commands.ChangeLevelPointerIndex` command so drag
        operations participate in the same undo and world-refresh workflow as
        other pointer edits.
        """

        source_index = self.selectedIndexes()[0].row()
        target_index = self.indexAt(event.position().toPoint()).row()

        self.undo_stack.push(ChangeLevelPointerIndex(self.world, source_index, target_index))

        self.update_content()

    def _save_level_pointer(self, row: int, column: int):
        """Translate one edited cell into the matching level-pointer command.

        This slot is the commit boundary between transient editor widgets and
        the persistent world-pointer model. It interprets the changed column,
        reads the delegate's committed value, and chooses the one undo command
        that can replay the same mutation later.

        Parameters
        ----------
        row : int
            Index of the edited level pointer inside ``self.world.level_pointers``.
        column : int
            Edited table column. Column ``0`` changes the object set, columns
            ``1`` and ``2`` change ROM addresses, and column ``3`` is ignored
            because it is a read-only position summary.

        Notes
        -----
        ``cellChanged`` fires after delegate widgets commit their values. This
        handler reads the committed widget state, normalizes pointer rows that
        would otherwise sit above :data:`smb3parse.levels.FIRST_VALID_ROW`, then
        pushes the matching undo command. The world's ``data_changed`` signal is
        emitted afterward so other tool-window views can repaint from the
        updated model.
        """

        if column == 3 or self.cellWidget(row, column) is None:
            return

        str_data = ""
        int_data = 0

        level_pointer = self.world.level_pointers[row]

        if column == 0:
            combo_box = typing.cast(QComboBox, self.cellWidget(row, column))
            str_data = combo_box.currentText()
        elif column in [1, 2]:
            spinner = typing.cast(Spinner, self.cellWidget(row, column))
            int_data = spinner.value()
        else:
            return

        if level_pointer.data.y < FIRST_VALID_ROW:
            level_pointer.data.y = FIRST_VALID_ROW

        if column == 0:
            self.undo_stack.push(SetObjectSet(level_pointer.data, OBJECT_SET_NAMES.index(str_data)))
        elif column == 1:
            self.undo_stack.push(SetLevelAddress(level_pointer.data, int_data))
        elif column == 2:
            self.undo_stack.push(SetEnemyAddress(level_pointer.data, int_data))
        else:
            return

        self.world.data_changed.emit()

    def update_content(self):
        """Rebuild the table rows from the active world-map pointer list.

        The refresh path resizes the table to the world's pointer count, blocks
        edit signals while rows are repopulated, and formats each pointer into
        the column layout expected by the delegates. The last column also
        reuses the shared icon helper so maintainers can correlate each table
        row with its position on the world map.
        """

        self.setRowCount(self.world.internal_world_map.level_count)

        self.blockSignals(True)

        for row, lp in enumerate(self.world.level_pointers):
            object_set_name = QTableWidgetItem(OBJECT_SET_NAMES[lp.data.object_set])

            hex_level_address = QTableWidgetItem(hex(lp.data.level_address))
            hex_enemy_address = QTableWidgetItem(hex(lp.data.enemy_address))
            pos = QTableWidgetItem(f"Screen {lp.data.screen}: x={lp.data.x}, y={lp.data.y}")

            self._set_map_tile_as_icon(pos, lp.get_position())

            self.setItem(row, 0, object_set_name)
            self.setItem(row, 1, hex_level_address)
            self.setItem(row, 2, hex_enemy_address)
            self.setItem(row, 3, pos)

        self.blockSignals(False)
