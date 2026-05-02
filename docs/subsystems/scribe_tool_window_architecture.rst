Scribe Tool Window Architecture
===============================

This page covers the tabbed auxiliary editing surface rooted at
:mod:`scribe.gui.tool_window`.

Problem and Context
-------------------

Scribe's world canvas edits several different kinds of things: raw map tiles,
level pointers, sprites, and lock or bridge objects. Putting every focused
editor into the main window would overload the canvas shell, but leaving them
uncoordinated would fragment selection and mode state. The tool-window package
solves that by grouping these editors into one floating, shared-mode surface.

Goals
-----

- Present a dedicated tool surface beside the main world view.
- Keep all tabs attached to the same active
  :class:`foundry.game.level.LevelRef.LevelRef`.
- Re-emit per-tool selection changes through one stable surface that the main
  window can wire into the world view.
- Clear stale list selections when the user switches editing modes.

Non-Goals
---------

- Replace the main window as the application shell.
- Own undo-command definitions; list widgets and dialogs ultimately hand off to
  the shared command layer.
- Own world rendering; only the tile picker renders its local block bank.

Current State
-------------

- :class:`scribe.gui.tool_window.tool_window.ToolWindow` is the composition
  point. It creates the tab widget, instantiates each tool, and bridges their
  selection signals outward.
- :class:`scribe.gui.tool_window.block_picker.BlockPicker` handles tile
  selection and tile-bank zooming.
- :class:`scribe.gui.tool_window.level_pointer_list.LevelPointerList`,
  :class:`scribe.gui.tool_window.sprite_list.SpriteList`, and
  :class:`scribe.gui.tool_window.locks_list.LocksList` present row-based
  editors for world-map objects.
- :class:`scribe.gui.tool_window.table_widget.TableWidget` and related
  delegates provide shared table behavior across those list-oriented tools.

Data Flow
---------

1. The main window constructs :class:`scribe.gui.tool_window.tool_window.ToolWindow`
   with the shared :class:`~foundry.game.level.LevelRef.LevelRef`.
2. Each tab reads the active world through that shared level reference.
3. Tab-local selection changes are re-emitted as
   :attr:`~scribe.gui.tool_window.tool_window.ToolWindow.tile_selected`,
   :attr:`~scribe.gui.tool_window.tool_window.ToolWindow.level_pointer_selection_changed`,
   :attr:`~scribe.gui.tool_window.tool_window.ToolWindow.sprite_selection_changed`,
   and
   :attr:`~scribe.gui.tool_window.tool_window.ToolWindow.locks_selection_changed`.
4. The main window connects those signals back into
   :class:`foundry.gui.visualization.world.WorldView.WorldView`, which updates
   the active canvas editing target or selection.

Control Flow
------------

1. :class:`scribe.gui.main_window.ScribeMainWindow` creates the tool window
   after the active world is loaded.
2. :class:`scribe.gui.tool_window.tool_window.ToolWindow` instantiates each tab
   and connects their outgoing selection signals.
3. When the user changes tabs, the tool window clears inactive list selections
   so only one editing mode remains highlighted at a time.
4. When the user chooses a tile or selects a row, the tool window re-emits that
   event and the world view reacts on the main canvas.

Architectural Decisions
-----------------------

Use one floating coordinator instead of independent auxiliary windows
   :class:`scribe.gui.tool_window.tool_window.ToolWindow` centralizes the
   secondary tools so the main editor only has to coordinate one companion
   window.

Share one level reference across all tabs
   Every tool reads from the same
   :class:`~foundry.game.level.LevelRef.LevelRef`, which keeps pointer, sprite,
   lock, and tile workflows synchronized to the currently loaded world.

Re-emit tool-local signals through the window boundary
   The main window depends on a small signal surface from
   :class:`~scribe.gui.tool_window.tool_window.ToolWindow` rather than on the
   internal API of each concrete tab widget.

Clear inactive selections on tab change
   Selection reset is deliberate: Scribe treats the tool window as one mode
   chooser for the shared world canvas, not as multiple concurrent list
   selections that should remain active simultaneously.

Read This Next
--------------

- Read :doc:`scribe_gui_architecture` for the main window that owns and wires
  this auxiliary surface.
- Read :doc:`scribe_commands_architecture` for the undoable mutations triggered
  after tool-driven edits.
- Read :class:`scribe.gui.tool_window.tool_window.ToolWindow` for the tab
  composition boundary.
- Continue into :class:`scribe.gui.tool_window.block_picker.BlockPicker` or the
  table-based list widgets when you need one specific tool workflow.
