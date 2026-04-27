"""Edit cross-world map allocation inside Scribe's tool window.

This module provides :class:`WorldOverview`, a table-backed editor that
reorders worlds and adjusts their screen and level-pointer budgets before the
changes are committed to the ROM through Scribe undo commands. Read next in
``scribe.gui.commands`` for the persistence steps that replay these edits, or
in ``scribe.gui.tool_window.table_widget`` for the shared table interaction
surface.

See Also
--------
scribe.gui.commands
    Undo commands that persist the staged world-allocation edits.
scribe.gui.tool_window.table_widget
    Shared drag-and-edit table surface used by the tool window widgets.
"""

import typing

from PySide6.QtCore import Signal, SignalInstance
from PySide6.QtGui import QDropEvent, QUndoStack
from PySide6.QtWidgets import QTableWidgetItem

from foundry.game.File import ROM
from foundry.game.level.LevelRef import LevelRef
from foundry.gui.widgets.Spinner import Spinner
from scribe.gui.commands import (
    AddLevelPointer,
    RemoveLevelPointer,
    SaveWorldsOnRedo,
    SaveWorldsOnUndo,
    SetScreenCount,
    SetStructureBlockAddress,
    SetTileDataOffset,
    SetWorldIndex,
    WorldDataStandIn,
)
from scribe.gui.tool_window.locks_list import NoneDelegate
from scribe.gui.tool_window.table_widget import SpinBoxDelegate, TableWidget
from smb3parse.constants import GAME_LEVEL_POINTER_COUNT, GAME_SCREEN_COUNT
from smb3parse.data_points import WorldMapData
from smb3parse.levels import WORLD_COUNT
from smb3parse.util.rom import Rom


class WorldOverview(TableWidget):
    """Present and stage world-allocation edits for a loaded overworld.

    The table mirrors one editable row per SMB3 world. Users can drag rows to
    swap world indexes, or change screen and level-pointer counts before the
    owning tool window decides whether to commit the staged edits. The class
    keeps those edits in :class:`~scribe.gui.commands.WorldDataStandIn`
    snapshots so the final write-back can be expressed as undoable commands
    instead of immediate ROM mutation.

    Parameters
    ----------
    parent
        Parent widget that owns the table in the tool window hierarchy.
    level_ref : foundry.game.level.LevelRef.LevelRef
        Shared level context used by :class:`TableWidget` to reach the active
        world map model.
    rom : smb3parse.util.rom.Rom
        ROM wrapper used to read world metadata for worlds other than the one
        currently open in the editor.

    Attributes
    ----------
    data_changed : PySide6.QtCore.SignalInstance
        Emitted after staged world data changes so surrounding widgets can
        refresh status and validation messaging.
    rom : smb3parse.util.rom.Rom
        ROM wrapper used when this table materializes stand-in world data.
    world_data_points : list[scribe.gui.commands.WorldDataStandIn]
        Mutable snapshots keyed by world index. The table edits these objects
        until :meth:`finalize` converts the staged state into undo commands.
    """

    data_changed: SignalInstance = Signal()

    def __init__(self, parent, level_ref: LevelRef, rom: Rom):
        """Build the staging table for world-order and size edits.

        This initializer creates the only mutable staging copy used by the
        world-overview workflow. Later drag, edit, validation, and save steps
        all operate on the stand-ins created here until :meth:`finalize`
        translates them into undo commands.

        Parameters
        ----------
        parent
            Parent widget that hosts the table.
        level_ref : foundry.game.level.LevelRef.LevelRef
            Shared level context that exposes the active world through the
            :class:`TableWidget` base class.
        rom : smb3parse.util.rom.Rom
            ROM wrapper used to load stand-in data for worlds outside the
            currently open world map.

        Notes
        -----
        Construction performs three stages that the rest of the workflow
        relies on:

        1. Build :attr:`world_data_points`, preserving the live edited world as
           a stand-in around ``self.world.data`` while loading every other
           world from ROM.
        2. Configure delegates so only numeric allocation columns are editable
           and they clamp to SMB3's legal ranges.
        3. Populate the table and connect change signals so later cell edits
           mutate the stand-ins rather than the ROM directly.

        The surrounding tool window treats this widget as a staging surface, so
        every later status check and commit step assumes these stand-ins remain
        the only mutable copy until :meth:`finalize` runs.
        """
        super(WorldOverview, self).__init__(parent, level_ref)

        self.rom = rom
        self.world_data_points: list[WorldDataStandIn] = []

        self.cellChanged.connect(self._change_data)

        for world_index in range(WORLD_COUNT - 1):
            if world_index == self.world.data.index:
                self.world_data_points.append(WorldDataStandIn(self.world.data))
                continue

            world_data_point = WorldMapData(rom, world_index)
            self.world_data_points.append(WorldDataStandIn(world_data_point))

        self.set_headers(["World Name", "Screen Count", "Level Count"])

        self.setItemDelegateForColumn(0, NoneDelegate(self))
        self.setItemDelegateForColumn(1, SpinBoxDelegate(self, minimum=1, maximum=4, base=10))
        self.setItemDelegateForColumn(2, SpinBoxDelegate(self, base=10))

        self.update_content()

    def dropEvent(self, event: QDropEvent) -> None:
        """Swap world indexes when the user drags one row onto another.

        The drop handler updates staged world ownership for two rows and then
        redraws the table so every later validation or save step sees the new
        world ordering.

        Parameters
        ----------
        event : PySide6.QtGui.QDropEvent
            Drop event whose source row and target row identify the two staged
            worlds that should exchange index positions.

        Notes
        -----
        The table does not reorder the backing list. Instead, it swaps the
        ``index`` stored on the stand-in objects and then redraws the table
        from those indexes. :meth:`finalize` later interprets those staged
        indexes when it emits undo commands, so drag-and-drop changes world
        ordering without mutating ROM-backed structures during the edit.
        """
        source_index = self.selectedIndexes()[0].row()
        target_index = self.indexAt(event.position().toPoint()).row()

        source_world = self.world_data_for(source_index)
        target_world = self.world_data_for(target_index)

        source_world.index = target_index
        target_world.index = source_index

        self.update_content()

        self.data_changed.emit()

    def world_data_for(self, world_index: int):
        """Resolve which staged world snapshot currently owns a table row.

        This lookup is the table's bridge from visible row order back to the
        mutable stand-in data that later validation and save operations
        consume.

        Parameters
        ----------
        world_index : int
            Target world index as displayed by the table.

        Returns
        -------
        scribe.gui.commands.WorldDataStandIn
            Stand-in whose ``index`` currently occupies ``world_index``.

        Raises
        ------
        LookupError
            Raised when the staged world list has become inconsistent and no
            stand-in claims that index.

        Notes
        -----
        Row ownership can change after drag-and-drop reordering, so the rest of
        the table workflow looks up stand-ins by their staged ``index`` rather
        than by list position.
        """
        for world_data in self.world_data_points:
            if world_data.index == world_index:
                return world_data
        else:
            raise LookupError(f"Couldn't find world with index {world_index}")

    def update_content(self):
        """Redraw the table from the staged world snapshots.

        Notes
        -----
        This method is used after initialization and after drag-reordering.
        Signals are blocked so table repaints do not recurse into
        :meth:`_change_data` while the staged values are being copied into the
        visible cells.
        """
        self.setRowCount(len(self.world_data_points))

        self.blockSignals(True)

        for world_number, world_data in enumerate(self.world_data_points, 1):
            row = world_data.index

            name_item = QTableWidgetItem(f"World {world_number}")
            screen_count_item = QTableWidgetItem(str(world_data.screen_count))
            level_count_item = QTableWidgetItem(str(world_data.level_count))

            self.setItem(row, 0, name_item)
            self.setItem(row, 1, screen_count_item)
            self.setItem(row, 2, level_count_item)

        self.blockSignals(False)

    def _change_data(self, row, column):
        """Apply one edited cell value back into the staged world snapshots.

        This slot keeps cell edits local to the stand-ins so the tool window
        can validate aggregate world usage before any command mutates ROM data.

        Parameters
        ----------
        row : int
            Row whose world allocation changed.
        column : int
            Column whose delegate committed a new value.

        Notes
        -----
        Column ``0`` is display-only, so only the numeric allocation columns
        mutate staged data. The method updates the matching
        :class:`WorldDataStandIn` and emits :attr:`data_changed` so the parent
        tool window can recompute status and validity messaging before commit.
        That keeps per-cell edits local to the staged snapshots while the
        larger save workflow decides whether the aggregate world layout is
        still valid.
        """
        world_index = row

        for world_data in self.world_data_points:
            if world_data.index == world_index:
                break
        else:
            return

        if column == 0:
            return

        widget = typing.cast(Spinner, self.cellWidget(row, column))
        data = widget.value()

        if column == 1:
            world_data.screen_count = data
        elif column == 2:
            world_data.level_count = data

        self.data_changed.emit()

    @property
    def level_count(self):
        """Total staged level-pointer count across all worlds.

        This aggregate is part of the table's validation boundary and feeds the
        status and save gating logic that surrounds the widget.

        Returns
        -------
        int
            Sum of the level-pointer budgets currently staged in the table.

        Notes
        -----
        The tool window uses this aggregate to decide whether staged world
        edits still fit within the ROM-wide level-pointer budget.
        """
        return sum([world_data.level_count for world_data in self.world_data_points])

    @property
    def screen_count(self):
        """Total staged screen count across all worlds.

        The tool window uses this aggregate to measure whether the staged world
        layout still fits the ROM-wide screen budget before commit.

        Returns
        -------
        int
            Sum of the screen budgets currently staged in the table.

        Notes
        -----
        The aggregate is a validation boundary rather than just a convenience
        accessor: it is compared against SMB3's global screen budget before the
        staged layout can be committed.
        """
        return sum([world_data.screen_count for world_data in self.world_data_points])

    @property
    def status_msg(self):
        """Summarize staged world usage against SMB3 global limits.

        The surrounding tool window displays this message while users reorder
        worlds or change counts, so it reflects staged state instead of saved
        ROM state.

        Returns
        -------
        str
            Human-readable status text used by the surrounding tool window to
            show remaining or exceeded screen and level-pointer capacity.

        Notes
        -----
        The message is derived from the staged aggregates, so it tracks drag
        reordering and per-cell edits before any undo command is created.
        """
        return (
            f"Your worlds have {self.screen_count}/{GAME_SCREEN_COUNT - 1} screens and "
            f"{self.level_count}/{GAME_LEVEL_POINTER_COUNT} level pointers."
        )

    def valid(self):
        """Report whether the staged world totals fit within SMB3 limits.

        Callers use this boolean as the final pre-save gate for the staged
        allocation workflow.

        Returns
        -------
        bool
            ``True`` when the staged screen count and level-pointer count do
            not exceed the ROM-wide maxima.

        Notes
        -----
        Callers use this gate before enabling the final save path, which keeps
        invalid world layouts from being translated into undo commands.
        """
        return self.screen_count <= GAME_SCREEN_COUNT - 1 and self.level_count <= GAME_LEVEL_POINTER_COUNT

    def finalize(self, undo_stack: QUndoStack):
        """Convert staged table edits into one undoable world-reorganization macro.

        This method is the commit boundary for the widget: it turns temporary
        table edits into the command sequence that rewrites world metadata and
        preserves undo and redo history.

        Parameters
        ----------
        undo_stack : PySide6.QtGui.QUndoStack
            Undo stack that receives the world-reorganization commands.

        Notes
        -----
        The table itself only edits :class:`WorldDataStandIn` snapshots.
        Finalization translates those snapshots into a command macro that:

        1. captures the pre-change world data for undo,
        2. reapplies world index ordering, screen counts, level-pointer counts,
           structure block addresses, and tile offsets in ROM order, and
        3. captures the post-change state for redo.

        The active world's tile cache is written before the macro so screen
        count changes can be undone against accurate tile data, then reread
        after the macro so the live world model reflects the committed layout.
        This method is the boundary where temporary table edits become
        persistence-aware undo history for the rest of Scribe.
        """
        if all(not world.changed for world in self.world_data_points):
            return

        # write tiles back into world map data object, so we can properly undo the screen count change
        self.world.write_tiles()
        undo_stack.beginMacro("Reorganize World Maps")

        undo_stack.push(SaveWorldsOnUndo(self.world_data_points))

        world_dict: dict[int, WorldDataStandIn] = {world.index: world for world in self.world_data_points}

        first_world = WorldMapData(ROM(), 0)

        structure_block_address = first_world.structure_block_address
        tile_data_offset_running_total = first_world.tile_data_offset

        for index in range(WORLD_COUNT - 1):
            world = world_dict[index]

            if world.data.index == self.world.data.index:
                world_map = self.world
            else:
                world_map = None

            undo_stack.push(SetWorldIndex(world.data, world.sprites, index))

            undo_stack.push(SetScreenCount(world.data, world.screen_count, world_map))

            if (diff := world.data.level_count - world.level_count) == 0:
                pass

            elif diff > 0:
                for _ in range(diff):
                    undo_stack.push(RemoveLevelPointer(world.data, world=world_map))
            else:
                for _ in range(abs(diff)):
                    undo_stack.push(AddLevelPointer(world.data, world_map))

            undo_stack.push(SetStructureBlockAddress(world.data, structure_block_address))
            structure_block_address += world.data.structure_block_size

            undo_stack.push(SetTileDataOffset(world.data, tile_data_offset_running_total))
            tile_data_offset_running_total += world.data.tile_data_size

        undo_stack.push(SaveWorldsOnRedo(self.world_data_points))

        undo_stack.endMacro()

        self.world.reread_tiles()

        self.world.data_changed.emit()
