"""Discovered-level table widgets for the level selector.

This module turns ``ROM.additional_data.found_levels`` into a sortable Qt table
with hover thumbnails and a small property-based API for dialogs that need a
selected layout address, enemy address, and object-set number. It sits between
automatic level discovery and the level-selector workflow, keeping row sorting
and tooltip rendering inside the table while exposing simple selection data to
the parent dialog.

See Also
--------
foundry.gui.dialogs.level_selector.LevelSelector
    Parent dialog that uses these widgets to choose one discovered level.
foundry.game.additional_data.LevelOrganizer
    Produces the discovered-level metadata consumed by this table.
"""

from PySide6.QtCore import QPoint
from PySide6.QtGui import QMouseEvent, Qt
from PySide6.QtWidgets import QLabel, QTableWidgetItem, QVBoxLayout, QWidget

from foundry import get_level_thumbnail, pixmap_to_base64
from foundry.game.File import ROM
from foundry.gui.widgets.table_widget import TableWidget
from smb3parse.constants import OBJECT_SET_NAMES
from smb3parse.util.parser import FoundLevel

LOST_LEVELS_INDEX = 8
OVERWORLD_MAPS_INDEX = 9


class FoundLevelWidget(QWidget):
    """List levels discovered from the active ROM.

    Found levels are produced by automatic level management and include current
    layout/enemy addresses, object set, jump-discovery information, and whether
    a level is world-specific. The widget exists so selector dialogs can work
    with that discovery output as one stable selection surface instead of
    learning parser metadata shape, Qt row sorting, or tooltip lookup details
    themselves.

    Attributes
    ----------
    _found_levels : list[FoundLevel]
        Discovered levels sorted for display.
    level_table : _FoundLevelTable
        Table used to select a discovered level.

    Notes
    -----
    This widget is only useful when automatic level management has already
    parsed the ROM. It presents those parser results as a selection surface for
    dialogs that need a discovered level address rather than a manually entered
    one. Parser output is copied and sorted here, ``_FoundLevelTable`` renders
    and reorders rows, and the widget properties translate the active row back
    into ROM addresses and object set numbers for callers. That keeps sorting
    and hover-preview behavior in the table while preserving a simple
    property-based API for parent dialogs. The widget therefore acts as the
    adapter between automatic-level-management output and dialog code that just
    wants "the selected discovered level". Long term, that keeps selector
    dialogs from learning about row sorting, tooltip generation, or parser
    metadata layout just to read back one chosen level. Future changes should
    preserve that containment: row presentation and metadata lookup live here,
    while the parent dialog should stay focused on the larger selection
    workflow rather than table bookkeeping.

    See Also
    --------
    _FoundLevelTable
        Handles sortable row display and hover thumbnails for the same data.
    foundry.gui.dialogs.level_selector.LevelSelector
        Embeds this widget in the broader level-selection workflow.

    Examples
    --------
    Parent dialogs use the widget as a thin adapter from table selection back
    to ROM addresses and object-set metadata::

        widget = FoundLevelWidget()
        level_address = widget.level_address
        enemy_address = widget.enemy_address

    The same widget also exposes the discovery context attached to the selected
    record without forcing callers to inspect table rows directly::

        object_set = widget.object_set_number
        world_number = widget.world_number

    That keeps caller code anchored to discovery metadata rather than the
    mechanics of row sorting or Qt item lookup::

        selected_layout = widget.level_address
        selected_enemy = widget.enemy_address
    """

    def __init__(self):
        """Create the discovered-level table.

        The table uses a copy of ``ROM.additional_data.found_levels`` so sorting
        and selection do not mutate persisted metadata, then exposes the table's
        selected row back out through lightweight address and object-set
        properties for parent dialogs.
        """
        super().__init__()

        # List of found levels
        self._found_levels = ROM.additional_data.found_levels.copy()
        self._found_levels.sort(key=lambda x: (x.world_number, x.level_offset))

        found_label = QLabel("Found Levels")
        self.level_table = _FoundLevelTable(self, self._found_levels)

        description_label = QLabel()

        description_label.setWordWrap(True)
        description_label.setText(
            "If the automatic Level management is active, the ROM is searched for all accessible Levels. Be it through "
            "an overworld, jumped to by another Level, or generic Levels, defined for every World (e.g. Coin Ship "
            "Levels). Inaccessible 'Lost' Levels cannot be found this way and are not listed here/have probably been "
            "overwritten to make space for more Levels."
        )

        found_level_layout = QVBoxLayout(self)
        found_level_layout.addWidget(found_label, 0)
        found_level_layout.addWidget(self.level_table, 1)
        found_level_layout.addWidget(description_label, 0)

    @property
    def level_address(self):
        """Expose the selected discovered level address.

        Parent dialogs use this property after table selection has already been
        translated through ``level_index``. It is the final adapter step from a
        sorted Qt table selection back to the ROM layout address needed to open
        the discovered level.

        Returns
        -------
        int
            ROM address of the selected level's header/object data.
        """
        return self._found_levels[self.level_table.level_index].level_offset

    @property
    def enemy_address(self):
        """Expose the selected discovered enemy-data address.

        Parent dialogs use this property after table selection has already been
        translated through ``level_index``. It keeps enemy-stream lookup tied
        to the same discovered-level record that produced the selected layout
        address.

        Returns
        -------
        int
            ROM address of the selected level's enemy/item data.
        """
        return self._found_levels[self.level_table.level_index].enemy_offset

    @property
    def object_set_number(self):
        """Expose the selected discovered object set number.

        Parent dialogs use this property after table selection has already been
        translated through ``level_index``. That keeps downstream parsing and
        rendering code aligned with the same discovered-level metadata row.

        Returns
        -------
        int
            Object set used to parse and render the selected level.
        """
        return self._found_levels[self.level_table.level_index].object_set_number

    @property
    def world_number(self):
        """Expose the selected discovered world number.

        Parent dialogs use this property after table selection has already been
        translated through ``level_index``. Dialogs use it when they need to
        preserve the discovery context that automatic level management attached
        to the selected record.

        Returns
        -------
        int
            One-based world number from discovered metadata.
        """
        return self._found_levels[self.level_table.level_index].world_number


class _FoundLevelTable(TableWidget):
    """Display discovered levels and hover thumbnails.

    The table stores the backing found-level index in ``UserRole`` so Qt
    sorting can reorder rows without breaking address lookups. That makes it
    the durable bridge between parser-owned discovery records and a user-facing
    Qt table whose visible row order is allowed to change.

    Parameters
    ----------
    parent : object
        Parent Qt widget that owns this object.
    levels : list[FoundLevel]
        Discovered levels to display.

    Attributes
    ----------
    _last_checked_level_index : int
        Last level index used for tooltip generation.
    _levels : list[FoundLevel]
        Discovered levels shown by the table.

    See Also
    --------
    FoundLevelWidget
        Owns the table and exposes the selected addresses to callers.
    """

    def __init__(self, parent, levels: list[FoundLevel]):
        """Create the sortable discovered-level table.

        The table stores the unsorted backing list separately from Qt's visible
        rows so sorting, hover previews, and selection can all resolve back to
        the same discovered-level records instead of drifting with row order.
        That separation is the long-lived contract for the widget: dialogs may
        let users sort the table however they want, but hover thumbnails,
        selection, and returned ROM addresses must still resolve to the same
        parser result that automatic level management discovered. Construction
        also primes the table headers, populates the visible rows, and selects
        the first discovered level so parent dialogs can query addresses
        immediately without running their own bootstrap pass. In other words,
        the constructor establishes the entire selection surface: once it
        returns, row metadata, thumbnail lookup, and exported address
        properties all point at the same discovered-level list. That is why the
        constructor owns both table bootstrap and the initial selection: later
        callers can rely on the widget being query-ready as soon as it exists.
        It is also the one place where Qt table behavior, cached parser
        metadata, and the default user selection are synchronized into one
        stable selection workflow for the parent dialog. In maintenance terms,
        the constructor establishes the contract that visible row order may
        change but the stored ``UserRole`` metadata still resolves every hover,
        selection, and exported property back to the same underlying
        ``FoundLevel`` record.

        Parameters
        ----------
        parent : object
            Parent Qt widget that owns this object.
        levels : list[FoundLevel]
            Discovered levels used to populate the metadata rows.
        """
        super().__init__(parent)

        self.setSortingEnabled(True)
        self.setMouseTracking(True)

        self.setEditTriggers(self.EditTrigger.NoEditTriggers)

        self._levels = levels
        self._last_checked_level_index = -1
        """The index of the last level we generated a thumbnail for."""

        self.set_headers(["World", "Object Set", "Level Addr.", "Enemy Addr.", "Jump Dest.", "World Specific"])

        self._update_content()

        self.selectRow(0)

    def _level_index_for_row(self, row):
        """Resolve a visible row back to the backing found-level index.

        Row order can change after Qt sorting, so callers use the stored
        ``UserRole`` metadata instead of assuming the visible row matches the
        original ``_levels`` order. This is the lookup that keeps hover
        thumbnails and selected addresses pinned to the correct found-level
        record.

        Parameters
        ----------
        row : int
            Visible table row.

        Returns
        -------
        int
            Level index represented by the table row.
        """
        return self.item(row, 0).data(Qt.ItemDataRole.UserRole)

    @property
    def level_index(self):
        """Resolve the selected row back to the backing found-level index.

        ``FoundLevelWidget`` uses this property as the single bridge from Qt row
        selection back to ROM addresses and object-set metadata.

        Returns
        -------
        int
            Index into ``_levels`` for the selected row.
        """
        return self._level_index_for_row(self.currentRow())

    def mouseMoveEvent(self, event: QMouseEvent):
        """Update the level thumbnail tooltip while hovering rows.

        The table delegates the expensive thumbnail work to ``_set_thumbnail``
        so hover handling can bail out quickly when the pointer stays on the
        same backing level while still participating in Qt's mouse-move flow.
        That keeps tooltip generation tied to backing discovered-level records
        instead of to transient row order, which matters once Qt sorting has
        rearranged the visible table. The event hook therefore acts as the
        lightweight hover stage: it preserves normal Qt mouse tracking while
        letting tooltip generation stay cached and row-order independent.

        Parameters
        ----------
        event : QMouseEvent
            Qt event delivered to the widget.

        Returns
        -------
        object
            Result returned by the Qt event handler, if any.
        """
        return self._set_thumbnail(event)

    def _set_thumbnail(self, event: QMouseEvent):
        """Generate a tooltip thumbnail for the hovered found level.

        Thumbnail generation is skipped if the hovered row still represents the
        same backing level index as the previous event, which avoids rebuilding
        identical thumbnails on every mouse-move event while the table remains
        visible.
        The method is the bridge from table hit-testing to preview generation:
        it translates the hovered Qt item back into the discovered-level record,
        asks the thumbnail helper for a rendered preview, and caches the last
        resolved backing index so repeated hover events stay cheap.

        Parameters
        ----------
        event : QMouseEvent
            Qt event delivered to the widget.
        """
        if not self.isVisible():
            # for some reason, even after the level selector is closed, the thumbnails still appear, but now in the
            # level view. no idea why.
            self.setToolTip("")
            return

        pos_plus_header = event.globalPosition() - QPoint(0, self.horizontalHeader().height() + 1)

        pos = self.mapFromGlobal(pos_plus_header.toPoint())

        # when double-clicking to select a level, this happened, killed the call and somehow made tooltips appear in the
        # level view, even after the level selector was cleaned up, so explicitly check that we still have an item
        if (item := self.itemAt(pos)) is None:
            return

        level_index = self._level_index_for_row(self.row(item))

        if level_index == self._last_checked_level_index:
            return

        self._last_checked_level_index = level_index

        if level_index == -1:
            self.setToolTip(None)
            return

        level = self._levels[level_index]

        image_data = get_level_thumbnail(
            level.object_set_number,
            level.level_offset,
            level.enemy_offset,
        )

        self.setToolTip(f"<img src='data:image/png;base64,{pixmap_to_base64(image_data)}'>")

    def _update_content(self):
        """Populate table rows from discovered level metadata.

        Each row displays world, object set, layout address, enemy address, and
        whether the level was found through jump or world-specific metadata.
        The method also stores each unsorted backing index in ``UserRole`` so
        later sorting cannot break the translation from a visible row back to
        the discovered-level record that hover previews and exported addresses
        depend on. It is the one projection step that turns parser metadata into
        stable table rows, selection metadata, and hover-preview inputs. In
        maintenance terms, this is the projection boundary between parser-owned
        discovery results and the Qt table state the selector dialog interacts
        with.
        """
        self.setRowCount(len(self._levels))

        self.blockSignals(True)

        for index, found_level in enumerate(self._levels):
            # sorting messes up the indexes, so save the level_index in found level list in the table time for world no
            world_table_item = QTableWidgetItem(f"World {found_level.world_number}")
            world_table_item.setData(Qt.ItemDataRole.UserRole, index)

            self.setItem(index, 0, world_table_item)
            self.setItem(index, 1, QTableWidgetItem(OBJECT_SET_NAMES[found_level.object_set_number]))
            self.setItem(index, 2, QTableWidgetItem(f"0x{found_level.level_offset:x}"))
            self.setItem(index, 3, QTableWidgetItem(f"0x{found_level.enemy_offset:0>4x}"))

            if found_level.found_as_jump and not found_level.found_in_world:
                cross_item = QTableWidgetItem("X")
                cross_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                self.setItem(index, 4, cross_item)
            else:
                no_cross_item = QTableWidgetItem("")
                no_cross_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                self.setItem(index, 4, no_cross_item)

            if found_level.is_world_specific:
                cross_item = QTableWidgetItem("X")
                cross_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                self.setItem(index, 5, cross_item)
            else:
                no_cross_item = QTableWidgetItem("")
                no_cross_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                self.setItem(index, 5, no_cross_item)

        self.blockSignals(False)
