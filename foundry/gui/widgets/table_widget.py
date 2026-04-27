"""Shared row-selection table widget for Foundry list and browser views.

This module provides :class:`TableWidget`, a thin ``QTableWidget`` wrapper that
standardizes the row-selection behavior used by Foundry dialogs and inspector
windows. Higher-level list widgets feed their column labels and row data into
this table, then consume its row-index signal as the user browses objects,
jumps, or other editor records. Keeping that selection plumbing here lets
browser-style widgets share one Qt setup path instead of rebuilding the same
table workflow in each dialog.

See Also
--------
foundry.gui.ObjectList
    Uses table-style browser widgets to surface level objects.
foundry.gui.JumpList
    Another list-oriented view that depends on consistent row selection.
"""

from PySide6.QtCore import Signal, SignalInstance
from PySide6.QtWidgets import QHeaderView, QSizePolicy, QTableWidget


class TableWidget(QTableWidget):
    """Provide a row-selection table with Foundry's common defaults.

    This widget wraps ``QTableWidget`` with the selection behavior used by
    Foundry's inspection dialogs and browser windows. It emits the selected row
    as a small helper signal so callers can react to row changes without
    re-reading the widget state themselves.

    Parameters
    ----------
    parent : QWidget
        Parent widget that owns the table.

    Attributes
    ----------
    selection_changed : SignalInstance
        Signal emitted with the selected row index after selection changes.
    """

    selection_changed: SignalInstance = Signal(int)

    def __init__(self, parent):
        """Initialize the shared row-selection table used by Foundry dialogs.

        The constructor establishes the shared selection lifecycle used by
        Foundry's browser-style widgets before they contribute headers or rows.
        It first applies the visual and single-row selection defaults that keep
        list dialogs behaving like one active-record browser, then configures
        the header so later ``set_headers`` and row-insertion calls can size
        columns around the caller's display data, and finally routes Qt's
        item-selection change signal through ``selected_row`` into
        ``selection_changed``. That signal bridge turns Qt's selection-model
        state into the stable row index consumed by object lists, jump lists,
        and similar inspector surfaces as the user moves through editor data.

        Parameters
        ----------
        parent : QWidget
            Parent widget that owns the table.
        """
        super(TableWidget, self).__init__(parent)

        self.setAlternatingRowColors(True)

        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.setSelectionBehavior(self.SelectionBehavior.SelectRows)
        self.setSelectionMode(self.SelectionMode.SingleSelection)

        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().setStretchLastSection(True)

        self.itemSelectionChanged.connect(lambda: self.selection_changed.emit(self.selected_row))

    def set_headers(self, headers: list[str]):
        """Apply the table's display columns for a specific browser view.

        The supplied labels become the visible column contract for whichever
        Foundry list or browser widget owns the table, and the columns are
        resized immediately so row data is readable without per-dialog header
        setup.

        Parameters
        ----------
        headers : list[str]
            Header labels in display order.
        """
        self.setColumnCount(len(headers))

        # TODO doesn't do anything?
        self.setHorizontalHeaderLabels(headers)
        self.resizeColumnsToContents()

    @property
    def selected_row(self):
        """Expose the active browser row as a single selection index.

        Foundry views built on :class:`TableWidget` treat the Qt selection model
        as a single-row browser surface. This property converts Qt's selected
        index list into the row number consumed by selection callbacks and
        returns ``-1`` when the table has no active row.

        Returns
        -------
        int
            Index of the first selected row, or ``-1`` when nothing is
            selected.
        """
        if self.selectedIndexes():
            return self.selectedIndexes()[0].row()
        else:
            return -1
