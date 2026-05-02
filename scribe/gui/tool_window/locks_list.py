"""Edit world-lock rows inside Scribe's tool window.

This module provides the table widget and item delegates that expose fortress
lock and bridge records as an editable grid. The table reads its row content
from a :class:`~foundry.game.level.LevelRef.LevelRef` world model, stages user
edits through delegate widgets, and forwards accepted changes into Scribe's
undoable command layer. In the tool-window workflow, the world view remains
the source of spatial truth while this table handles metadata edits such as
replacement tiles and lock indices, then repaints itself after model updates.

See Also
--------
scribe.gui.tool_window.table_widget
    Shared world-table base classes and delegate helpers used by tool-window
    editors.
scribe.gui.commands
    Undoable command objects that persist replacement-tile and lock-index
    edits back into the world model.
"""

import typing

from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtWidgets import QStyledItemDelegate, QTableWidgetItem, QWidget

from foundry.game.gfx.block_cache import get_worldmap_tile
from foundry.game.level.LevelRef import LevelRef
from foundry.gui.localization import tr
from foundry.gui.widgets.Spinner import Spinner
from foundry.gui.windows.BlockViewer import BlockBank
from scribe.gui.commands import ChangeLockIndex, ChangeReplacementTile
from scribe.gui.tool_window.table_widget import (
    DialogDelegate,
    SpinBoxDelegate,
    TableWidget,
)
from smb3parse.constants import FORTRESS_FX_COUNT

TR_CONTEXT = "ScribeLocksList"


class LocksList(TableWidget):
    """Display and edit fortress lock records for the active world.

    The widget adapts ``world.locks_and_bridges`` into one row per lock entry.
    Editable columns hand off changes to undoable command objects, while the
    read-only columns explain the Boom Boom slot range and the map position
    associated with each lock.

    Notes
    -----
    ``LocksList`` is intentionally a projection of world data, not an
    alternate owner of it. The row order, Boom Boom slot ranges, and map
    positions all come from ``world.locks_and_bridges`` and the world-view
    model; this table must keep reflecting that ordering instead of caching its
    own copy. Edits therefore flow through undo commands and a follow-up
    ``data_changed`` emission so the table, world view, and persistence layer
    all observe the same mutation boundary.

    See Also
    --------
    BlockBankDelegate
        Delegate that turns replacement-tile edits into block-bank selections.
    NoneDelegate
        Delegate that keeps derived lock metadata in display-only mode.

    Parameters
    ----------
    parent
        Parent widget that owns the tool-window table.
    level_ref : LevelRef
        Shared level reference that supplies the active world model, undo
        stack, and data-changed signal used by the table.
    """

    def __init__(self, parent, level_ref: LevelRef):
        """Initialize the lock table and wire its edit delegates.

        The table inherits the shared world-table setup from
        :class:`~scribe.gui.tool_window.table_widget.TableWidget`, then narrows
        editing to lock-specific columns. Replacement-tile edits use a block
        picker, lock-index edits use a bounded spinner, and the remaining
        columns are kept informational so row edits continue to flow through
        the undo stack rather than ad hoc widget state.

        Parameters
        ----------
        parent
            Parent widget that owns the table in the tool window.
        level_ref : LevelRef
            Shared level reference whose world object supplies lock rows and
            receives undoable edits.
        """

        super(LocksList, self).__init__(parent, level_ref)

        self.setDragDropMode(self.DragDropMode.NoDragDrop)

        self.cellChanged.connect(self._save_fortress_fx)

        self.set_headers(
            [
                tr(TR_CONTEXT, "replacement_tile", "Replacement Tile"),
                tr(TR_CONTEXT, "lock_index", "Lock Index"),
                tr(TR_CONTEXT, "boom_boom_y_positions", "Boom Boom Y Positions"),
                tr(TR_CONTEXT, "map_position", "Map Position"),
            ]
        )

        self.setItemDelegateForColumn(0, BlockBankDelegate(self))
        self.setItemDelegateForColumn(1, SpinBoxDelegate(self, maximum=FORTRESS_FX_COUNT - 1))
        self.setItemDelegateForColumn(2, NoneDelegate(self))
        self.setItemDelegateForColumn(
            3,
            self._make_position_dialog_delegate(),
        )

        self.update_content()

    def retranslate_ui(self) -> None:
        """Refresh headers and position rows after a language change.

        The refresh updates localized table headers and the informational
        position delegate, then rebuilds rows from the world model while
        restoring selection. Replacement-tile ids, lock indexes, and Boom Boom
        slot ranges remain encoded data, not translated display state.
        """
        selected_row = self.selected_row
        self.set_headers(
            [
                tr(TR_CONTEXT, "replacement_tile", "Replacement Tile"),
                tr(TR_CONTEXT, "lock_index", "Lock Index"),
                tr(TR_CONTEXT, "boom_boom_y_positions", "Boom Boom Y Positions"),
                tr(TR_CONTEXT, "map_position", "Map Position"),
            ]
        )
        self.setItemDelegateForColumn(3, self._make_position_dialog_delegate())
        self.update_content()
        if 0 <= selected_row < self.rowCount():
            self.selectRow(selected_row)

    def _make_position_dialog_delegate(self) -> DialogDelegate:
        """Create the read-only map-position guidance delegate.

        The delegate protects the state boundary between tabular fortress FX
        metadata and map placement. Spatial movement stays in the world view
        workflow, while this table commits only replacement-tile and lock-index
        edits through undoable commands.

        Returns
        -------
        DialogDelegate
            Informational delegate explaining that fortress FX placement is
            owned by drag operations in the world view.
        """
        return DialogDelegate(
            self,
            tr(TR_CONTEXT, "no_can_do", "No can do"),
            tr(
                TR_CONTEXT,
                "help.fortress_fx_dragging",
                "You can move Fortress FX by dragging them around in the WorldView. Make sure they are shown in the View Menu.",
            ),
        )

    def _save_fortress_fx(self, row: int, column: int):
        """Convert an edited cell into an undoable world-lock command.

        The table only commits editable columns. Column ``0`` stages the
        replacement-block choice from the embedded block picker, and column
        ``1`` stages the selected lock index from the spinner delegate. Both
        cases push a command onto the shared undo stack so table edits stay in
        sync with the rest of Scribe's world-edit workflow.

        Parameters
        ----------
        row : int
            Row whose backing lock record was edited.
        column : int
            Edited column index within the lock table.
        """

        if column in [2, 3]:
            return

        lock = self.world.locks_and_bridges[row]

        if column == 0:
            block_bank = typing.cast(BlockBank, self.cellWidget(row, column))
            data = block_bank.last_clicked_index

            self.undo_stack.push(ChangeReplacementTile(self.world, lock.data.index, data))

        elif column == 1:
            spinner = typing.cast(Spinner, self.cellWidget(row, column))
            data = spinner.value()

            self.undo_stack.push(ChangeLockIndex(self.world, lock, data))

        else:
            return

        self.world.data_changed.emit()

    def update_content(self):
        """Rebuild every table row from the active world's lock records.

        The refresh blocks table signals so repopulating cells does not look
        like user edits. Each row renders the replacement tile, lock index,
        Boom Boom slot range, and map position for one lock entry, then reuses
        the shared map-tile icon helper so the table stays visually aligned
        with the world-view editing surface.

        Notes
        -----
        The method recomputes every display cell from world state
        rather than trying to patch rows incrementally. That keeps the visual
        representation aligned with undo, drag-based world-view edits, and any
        other command that changes ``locks_and_bridges`` ordering or contents.
        Signal blocking is part of that contract: a repaint must not re-enter
        :meth:`_save_fortress_fx` and enqueue duplicate commands.
        """

        self.setRowCount(len(self.world.locks_and_bridges))

        self.blockSignals(True)

        for index, fortress_fx in enumerate(self.world.locks_and_bridges):
            replacement_tile = QTableWidgetItem(hex(fortress_fx.data.replacement_block_index))

            block_icon = QPixmap(self.iconSize())
            painter = QPainter(block_icon)
            get_worldmap_tile(fortress_fx.data.replacement_block_index).draw(painter, 0, 0, self.iconSize().width())
            painter.end()

            replacement_tile.setIcon(block_icon)

            fortress_index = QTableWidgetItem(hex(fortress_fx.data.index))

            boom_boom_pos = QTableWidgetItem(f"{0x10 + 0x10 * index:#x} - {0x20 + 0x10 * index - 1:#x}")
            pos = QTableWidgetItem(
                tr(TR_CONTEXT, "screen_screen_x_x_y_y", "Screen {screen}: x={x}, y={y}").format(
                    screen=fortress_fx.data.screen,
                    x=fortress_fx.data.x,
                    y=fortress_fx.data.y,
                )
            )

            self._set_map_tile_as_icon(pos, fortress_fx.get_position())

            self.setItem(index, 0, replacement_tile)
            self.setItem(index, 1, fortress_index)
            self.setItem(index, 2, boom_boom_pos)
            self.setItem(index, 3, pos)

        self.blockSignals(False)


class BlockBankDelegate(QStyledItemDelegate):
    """Embed the block-bank picker used for replacement-tile edits.

    The delegate creates the same block viewer used elsewhere in the editor,
    but presents it as an in-cell editor for the replacement-tile column so
    lock metadata edits reuse the same tile-selection surface as the world map.

    Notes
    -----
    The delegate preserves a workflow boundary between Qt's item-editor API
    and Scribe's block-selection UI. Future replacements still need to behave
    like a single completed cell edit from the table's perspective, because
    :class:`LocksList` listens for ``cellChanged`` and translates that event
    into one undoable replacement-tile command.
    """

    def createEditor(self, parent: QWidget, option, index) -> QWidget:
        """Create the replacement-tile picker for a table cell.

        Qt asks the delegate for an editor before a replacement-tile edit is
        committed. Returning a standalone :class:`BlockBank` keeps the tile
        selection workflow consistent with the world-view tooling while still
        letting the table own when the edit starts and finishes.

        Parameters
        ----------
        parent : QWidget
            Parent widget supplied by Qt for the editor lifecycle.
        option
            Style information for the edited cell.
        index
            Model index identifying the edited cell.

        Returns
        -------
        QWidget
            A block-bank picker that hides itself after a tile is chosen so
            the table can treat the selection as one completed cell edit.
        """

        block_bank = BlockBank(None)
        block_bank.clicked.connect(block_bank.hide)

        return block_bank

    def setEditorData(self, editor, index):
        """Show the block-bank picker when editing begins.

        Qt calls this hook after creating the editor for the replacement-tile
        cell. Showing the picker here keeps the block-bank popup synchronized
        with the table's edit lifecycle instead of requiring the row widget to
        manage its own visibility.

        Parameters
        ----------
        editor
            Editor widget created by :meth:`createEditor`.
        index
            Model index for the edited cell.
        """

        editor.show()


class NoneDelegate(QStyledItemDelegate):
    """Disable direct editing for read-only lock-table columns.

    The delegate keeps informational columns inside Qt's delegate pipeline
    while making it explicit that Boom Boom position ranges and map-position
    summaries are derived display data rather than editable lock properties.

    Notes
    -----
    This class documents a deliberate boundary in the tool-window workflow:
    some lock attributes are edited in the table, while spatial placement
    remains owned by the world view. Keeping a dedicated no-op delegate here
    makes that split visible in code and helps prevent later refactors from
    turning derived display columns into accidental write paths.
    """

    def createEditor(self, parent: QWidget, option, index) -> QWidget:
        """Refuse to create an editor for a read-only cell.

        The tool window still routes edit attempts through the delegate API for
        every column. Returning ``None`` here makes the read-only boundary
        explicit so map-position and Boom Boom range columns cannot drift into
        editable state when the shared table infrastructure is reused.

        Parameters
        ----------
        parent : QWidget
            Parent widget supplied by Qt for the editor lifecycle.
        option
            Style information for the edited cell.
        index
            Model index identifying the edited cell.

        Returns
        -------
        QWidget
            ``None`` so Qt leaves the column in display mode and routes lock
            edits through the dedicated editable delegates instead.
        """

        return None

    def setEditorData(self, editor, index):
        """Accept Qt's edit callback without mutating read-only state.

        Qt may still invoke the delegate hook while resolving an attempted
        edit. Doing nothing preserves the display-only contract for the column
        while letting the table participate in the normal delegate lifecycle.

        Parameters
        ----------
        editor
            Editor widget that Qt would have supplied for the cell.
        index
            Model index for the edited cell.
        """

        pass
