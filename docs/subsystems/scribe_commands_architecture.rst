Scribe Commands Architecture
============================

This page covers the undo-command family rooted at :mod:`scribe.gui.commands`.

Problem and Context
-------------------

Scribe edits ROM-backed overworld state through interactive gestures and dialog
submissions, but those changes must remain undoable, redoable, and compatible
with Foundry's lazy additional-data refresh behavior. The command layer is the
replay boundary that converts GUI intent into durable world-map mutations.

Goals
-----

- Express overworld edits as :class:`PySide6.QtGui.QUndoCommand` objects.
- Preserve enough pre-edit state to restore tiles, map objects, and world data
  accurately on undo.
- Keep ROM additional-data caches marked dirty when command effects can change
  parse-sensitive structures.
- Support both immediate canvas edits and deferred dialog-finalization flows.

Non-Goals
---------

- Own the top-level GUI routing; the main window, menus, and dialogs decide
  when commands should be pushed.
- Own staging-table validation; that belongs to
  :class:`scribe.gui.world_overview.WorldOverview`.
- Render the world map or host selection state directly.

Current State
-------------

- :mod:`scribe.gui.commands` groups command families for tile placement and
  movement, world-map object movement, direct data-point edits, and world-save
  helpers.
- :class:`scribe.gui.commands.DirtyAdditionalDataMixin` wraps commands whose
  effects require Foundry's additional-data cache to be refreshed.
- Commands such as :class:`scribe.gui.commands.MoveTile` and
  :class:`scribe.gui.commands.MoveMapObject` snapshot pre-edit state during
  construction, then replay the edit through ``redo()`` and restore it through
  ``undo()``.
- World-overview save helpers translate staged
  :class:`scribe.gui.commands.WorldDataStandIn` state into a sequence of
  commands rather than bypassing the undo stack.

Data Flow
---------

1. A GUI surface such as :class:`foundry.gui.visualization.world.WorldView`,
   :class:`scribe.gui.edit_world_info.EditWorldInfo`, or
   :class:`scribe.gui.world_overview.WorldOverview` identifies a mutation the
   user wants to keep.
2. It constructs one or more command objects, capturing any before-state needed
   for later undo.
3. The owning :class:`PySide6.QtGui.QUndoStack` pushes the command, invoking
   ``redo()`` as the authoritative mutation step.
4. Command logic updates :class:`foundry.game.level.WorldMap.WorldMap`,
   world-map objects, or ROM-backed data-point wrappers and, when needed,
   marks :attr:`foundry.game.File.ROM.additional_data` dirty.
5. Undo and redo later replay the same command boundary instead of rerunning
   GUI logic.

Control Flow
------------

1. The GUI determines the editing intent and chooses the command class.
2. Command construction captures endpoints, previous values, selected object
   identity, or staged world metadata.
3. The undo stack invokes ``redo()`` immediately on push.
4. Subsequent undo or redo requests from the shared stack re-enter the command
   directly, bypassing the original menu, dialog, or gesture code.

Architectural Decisions
-----------------------

Use command objects as the mutation boundary
   Scribe keeps world edits undoable by making the command layer, rather than
   the GUI layer, the place where real state changes happen.

Snapshot before-state during initialization
   Tile types, object positions, and world metadata are captured before the
   first mutation so undo can restore the exact prior state rather than
   reconstructing it heuristically.

Separate cache-dirty behavior into a mixin
   :class:`scribe.gui.commands.DirtyAdditionalDataMixin` keeps Foundry refresh
   concerns reusable across multiple command classes instead of scattering ROM
   cache writes through unrelated mutation logic.

Support deferred commit workflows
   The command family includes save helpers for staged world-overview edits so
   validation-heavy dialogs can accumulate proposed changes first and only then
   turn them into replayable state transitions.

Read This Next
--------------

- Read :doc:`scribe_gui_architecture` for the surfaces that enqueue these
  commands.
- Read :doc:`scribe_tool_window_architecture` for the widgets that select
  targets later mutated through command replay.
- Read :class:`foundry.gui.visualization.world.WorldView.WorldView` to trace
  drag and placement gestures into command creation.
- Read :class:`foundry.game.level.WorldMap.WorldMap` when you need the mutable
  world model that command ``redo()`` and ``undo()`` operate on.
