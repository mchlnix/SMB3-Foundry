Scribe GUI Architecture
=======================

This page is the architecture entry point for Scribe's top-level GUI package,
centered on :mod:`scribe.gui`, :mod:`scribe.gui.main_window`,
:mod:`scribe.gui.world_overview`, and the dialogs and context-menu helpers that
hang off that shell.

Problem and Context
-------------------

Scribe edits SMB3 overworld data inside a Qt application, but the actual world
state lives in ROM-backed models and shared Foundry editor infrastructure. The
GUI package has to turn ROM loading, world selection, tool-window interaction,
canvas gestures, and save or export actions into one coherent editor session
without duplicating Foundry's base-window services.

Goals
-----

- Provide one editor shell for opening a ROM, loading a world, editing it, and
  saving or exporting the result.
- Keep all GUI surfaces attached to the same active
  :class:`foundry.game.level.LevelRef.LevelRef` and
  :class:`PySide6.QtGui.QUndoStack`.
- Separate short-lived workflow branches such as settings and world-info
  editing from the persistent shell.
- Keep cross-world staging workflows available without forcing the main canvas
  to understand allocation tables directly.

Non-Goals
---------

- Reimplement Foundry's generic ROM-window infrastructure inside Scribe.
- Own low-level world rendering logic; that remains in
  :class:`foundry.gui.visualization.world.WorldView`.
- Own every focused editing surface; menu, command, and tool-window families
  are delegated to their own packages.

Current State
-------------

- :class:`scribe.gui.main_window.ScribeMainWindow` is the composition root.
  It loads the ROM, constructs the world view, owns the undo stack, and wires
  menus, shortcuts, and the floating tool window around the shared
  :class:`~foundry.game.level.LevelRef.LevelRef`.
- :class:`scribe.gui.world_overview.WorldOverview` is the cross-world staging
  surface for screen-count, level-count, and world-order edits. It does not
  write immediately to ROM-backed world data; instead it edits stand-ins that
  are later finalized as undo commands.
- :class:`scribe.gui.edit_world_info.EditWorldInfo` is the modal workflow for
  world metadata and staged world-overview changes. It previews some changes
  directly on the active world while deferring the final persisted transaction
  to the undo stack.
- :mod:`scribe.gui.settings_dialog`, :mod:`scribe.gui.about_window`, and
  :mod:`scribe.gui.world_view_context_menu` provide secondary workflow surfaces
  that plug into the main window rather than owning independent editor state.

Data Flow
---------

1. :class:`scribe.gui.main_window.ScribeMainWindow` opens a ROM and populates
   the shared :class:`~foundry.game.level.LevelRef.LevelRef` with the active
   :class:`foundry.game.level.WorldMap.WorldMap`.
2. That level reference is passed to the world view, tool window, and any
   world-focused dialogs so all surfaces read the same active world model.
3. For cross-world editing, :class:`~scribe.gui.edit_world_info.EditWorldInfo`
   creates :class:`scribe.gui.world_overview.WorldOverview`, which materializes
   :class:`scribe.gui.commands.WorldDataStandIn` snapshots instead of mutating
   the ROM-facing structures directly.
4. Accepted dialog changes become undo commands, which then write back into the
   active world model and ROM-backed data points through the shared stack.

Control Flow
------------

1. Startup enters through :class:`scribe.gui.main_window.ScribeMainWindow`,
   which subclasses :class:`foundry.gui.MainWindow.MainWindow`.
2. The main window constructs the persistent collaborators first: the shared
   level reference, the undo stack, the world view, and the tool window.
3. Menus, shortcuts, and the world-view context menu route user actions back
   into that shell, where they are delegated to the world view, menu families,
   or command objects.
4. Modal branches such as
   :class:`scribe.gui.edit_world_info.EditWorldInfo` temporarily take over the
   workflow, then rejoin the main session by pushing undo commands or emitting
   refresh signals when they close.

Architectural Decisions
-----------------------

Use Foundry's base main window
   Scribe subclasses :class:`foundry.gui.MainWindow.MainWindow` rather than
   forking ROM-open, ROM-save, update-check, and emulator-launch behavior.

One shared level reference and undo stack
   The shell keeps all persistent surfaces attached to one
   :class:`~foundry.game.level.LevelRef.LevelRef` and one
   :class:`~PySide6.QtGui.QUndoStack`, which avoids split editor state between
   the canvas, menus, and tool window.

Stage cross-world edits before persistence
   :class:`scribe.gui.world_overview.WorldOverview` edits stand-ins first so
   aggregate world-allocation validation can happen before any undo command
   mutates ROM-backed records.

Keep focused workflows out of the shell
   World metadata editing, settings, support dialogs, and context-menu actions
   are factored into their own modules so the main window stays a coordinator
   instead of absorbing every narrow workflow.

Read This Next
--------------

- Read :doc:`scribe_commands_architecture` to follow how GUI requests become
  undoable mutations.
- Read :doc:`scribe_tool_window_architecture` for the auxiliary editing surface
  that chooses tiles, pointers, sprites, and locks.
- Read :doc:`scribe_menus_architecture` to trace menu-triggered workflow and
  settings persistence.
- Read :class:`foundry.gui.visualization.world.WorldView.WorldView` when the
  next question is how the active world is rendered and edited on the canvas.
- Keep :doc:`../api/scribe_gui` open beside this page when you need generated
  code reference for the Scribe GUI modules.
