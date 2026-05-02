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

See Also
--------
scribe.gui.commands
    Undo command implementations that commit level-pointer edits.
scribe.gui.tool_window.table_widget
    Shared table and delegate infrastructure used by Scribe tool windows.
"""

import typing

from PySide6.QtCore import Qt
from PySide6.QtGui import QDropEvent
from PySide6.QtWidgets import QComboBox, QTableWidgetItem

from foundry.game.level.LevelRef import LevelRef
from foundry.gui.localization import tr, tr_data_name
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

TR_CONTEXT = "ScribeLevelPointerList"


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

        self.set_headers(
            [
                tr(TR_CONTEXT, "object_set", "Object Set"),
                tr(TR_CONTEXT, "level_offset", "Level Offset"),
                tr(TR_CONTEXT, "enemy_item_offset", "Enemy/Item Offset"),
                tr(TR_CONTEXT, "map_position", "Map Position"),
            ]
        )

        self.setItemDelegateForColumn(
            0,
            DropdownDelegate(
                self,
                [tr_data_name("ObjectSet", object_set_name) for object_set_name in OBJECT_SET_NAMES],
                data=list(range(len(OBJECT_SET_NAMES))),
            ),
        )
        self.setItemDelegateForColumn(1, SpinBoxDelegate(self))
        self.setItemDelegateForColumn(2, SpinBoxDelegate(self))
        self.setItemDelegateForColumn(
            3,
            self._make_position_dialog_delegate(),
        )

        self.update_content()

    def retranslate_ui(self) -> None:
        """Refresh headers and dropdown labels after a language change.

        The refresh rebuilds display text, object-set dropdown labels, and the
        read-only position delegate while preserving the selected row and the
        stable object-set ids stored in ``Qt.UserRole``. Rebuilding rows after
        delegate replacement keeps visible labels localized without changing
        pointer identity or undo-stack state.
        """
        selected_row = self.selected_row
        self.set_headers(
            [
                tr(TR_CONTEXT, "object_set", "Object Set"),
                tr(TR_CONTEXT, "level_offset", "Level Offset"),
                tr(TR_CONTEXT, "enemy_item_offset", "Enemy/Item Offset"),
                tr(TR_CONTEXT, "map_position", "Map Position"),
            ]
        )
        self.setItemDelegateForColumn(
            0,
            DropdownDelegate(
                self,
                [tr_data_name("ObjectSet", object_set_name) for object_set_name in OBJECT_SET_NAMES],
                data=list(range(len(OBJECT_SET_NAMES))),
            ),
        )
        self.setItemDelegateForColumn(3, self._make_position_dialog_delegate())
        self.update_content()
        if 0 <= selected_row < self.rowCount():
            self.selectRow(selected_row)

    def _make_position_dialog_delegate(self) -> DialogDelegate:
        """Create the read-only map-position guidance delegate.

        The delegate marks a deliberate workflow boundary between table
        metadata edits and map-placement state. Position changes stay owned by
        the world view so drag operations can commit through the undo stack and
        preserve level-pointer identity.

        Returns
        -------
        DialogDelegate
            Informational delegate explaining that spatial pointer movement is
            owned by the world view, not by direct table-cell editing.
        """
        return DialogDelegate(
            self,
            tr(TR_CONTEXT, "no_can_do", "No can do"),
            tr(
                TR_CONTEXT,
                "help.level_pointer_dragging",
                "You can move level pointers by dragging them around in the WorldView. Make sure they are shown in the View Menu.",
            ),
        )

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

        int_data = 0

        level_pointer = self.world.level_pointers[row]

        if column == 0:
            combo_box = typing.cast(QComboBox, self.cellWidget(row, column))
            int_data = int(combo_box.currentData(Qt.ItemDataRole.UserRole))
        elif column in [1, 2]:
            spinner = typing.cast(Spinner, self.cellWidget(row, column))
            int_data = spinner.value()
        else:
            return

        if level_pointer.data.y < FIRST_VALID_ROW:
            level_pointer.data.y = FIRST_VALID_ROW

        if column == 0:
            self.undo_stack.push(SetObjectSet(level_pointer.data, int_data))
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
            object_set_name = QTableWidgetItem(tr_data_name("ObjectSet", OBJECT_SET_NAMES[lp.data.object_set]))
            object_set_name.setData(Qt.ItemDataRole.UserRole, lp.data.object_set)

            hex_level_address = QTableWidgetItem(hex(lp.data.level_address))
            hex_enemy_address = QTableWidgetItem(hex(lp.data.enemy_address))
            pos = QTableWidgetItem(
                tr(TR_CONTEXT, "screen_screen_x_x_y_y", "Screen {screen}: x={x}, y={y}").format(
                    screen=lp.data.screen,
                    x=lp.data.x,
                    y=lp.data.y,
                )
            )

            self._set_map_tile_as_icon(pos, lp.get_position())

            self.setItem(row, 0, object_set_name)
            self.setItem(row, 1, hex_level_address)
            self.setItem(row, 2, hex_enemy_address)
            self.setItem(row, 3, pos)

        self.blockSignals(False)
