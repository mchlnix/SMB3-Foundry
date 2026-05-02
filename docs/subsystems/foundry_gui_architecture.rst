Foundry GUI Architecture
========================

Problem and Context
-------------------

The :mod:`foundry.gui` family is the editor-facing shell for Foundry. It has to
keep Qt widgets, ROM-backed level state, undoable edits, and specialized
dialogs coordinated without letting any one workflow own the whole
application. Maintainers usually land here when a user gesture, dialog commit,
or repaint does not match the underlying level state.

Goals
-----

- Keep :class:`foundry.gui.FoundryMainWindow` as the application shell that
  owns session-level coordination.
- Translate gestures and dialog commits into command or model operations rather
  than embedding business logic in random widgets.
- Keep visualization, inspectors, menus, and dialogs split by workflow role so
  changes stay local.
- Preserve a predictable handoff into :mod:`foundry.game`,
  :mod:`foundry.features`, and the command stack.

Non-Goals
---------

- Reimplement SMB3 parsing or rendering policy inside the Qt layer.
- Make every widget reusable in isolation.
- Treat the package as one deeply nested widget tree with a single ownership
  path.

Current State
-------------

The current GUI architecture is centered on
:class:`foundry.gui.FoundryMainWindow`, which owns the active ROM session, the
level or world surface, and the handoff into dialogs, menus, and auxiliary
windows. :mod:`foundry.gui.visualization` converts user gestures into editor
operations. :mod:`foundry.gui.commands` preserves those operations as replayable
mutations. Dialog-heavy workflows live under :mod:`foundry.gui.dialogs` and
:mod:`foundry.gui.level_settings`, while denser read-only or debugging surfaces
live under :mod:`foundry.gui.windows` and :mod:`foundry.gui.widgets`.

Data Flow
---------

1. :class:`foundry.gui.FoundryMainWindow` exposes the active level, world, ROM,
   and editor settings.
2. Views such as :class:`foundry.gui.visualization.level.LevelView` and
   :class:`foundry.gui.visualization.world.WorldView` read that state and stage
   selections, drag targets, and hover information.
3. Dialogs and inspector widgets gather focused user input and convert it into
   command or model updates.
4. Command producers hand changes to :mod:`foundry.gui.commands`, which in
   turn mutate :mod:`foundry.game` model objects.
5. Updated model and render state flows back into the visualization and window
   surfaces for repaint and inspection.

Control Flow
------------

Startup enters through :class:`foundry.gui.FoundryMainWindow`, which wires the
menu bar, visualization surfaces, and feature hooks. Interactive control then
branches by workflow:

- Gestures in :class:`foundry.gui.visualization.MainView` subclasses become
  selection, drag, resize, or placement operations.
- Dialog acceptance in :mod:`foundry.gui.dialogs` or
  :mod:`foundry.gui.level_settings` becomes a command-producing commit point.
- Menu actions dispatch into ROM, view, help, or tool workflows.
- Auxiliary windows read already-owned state rather than becoming new sources
  of truth.

Architectural Decisions
-----------------------

- The shell-model boundary is explicit: GUI modules coordinate, while
  :mod:`foundry.game` owns long-lived ROM-backed state.
- View classes are workflow translators, not the canonical store for object or
  level data.
- Command generation is favored over ad hoc mutation because undo, redo, and
  replay are first-class editor behaviors.
- Focused dialogs and inspector windows are split into smaller modules so one
  feature pass does not require understanding the entire shell.
- Cross-cutting behaviors such as update checking and ROM reload stay in
  :mod:`foundry.features` even when the GUI triggers them.

Read This Next
--------------

- Start with :class:`foundry.gui.FoundryMainWindow` for shell ownership,
  session lifecycle, and major workflow routing.
- Continue to :class:`foundry.gui.visualization.level.LevelView` and
  :class:`foundry.gui.visualization.MainView` for gesture translation.
- Read :mod:`foundry.gui.commands` when you need the undoable mutation layer.
- Follow :mod:`foundry.gui.level_settings.level_settings_dialog` and the
  surrounding mixins for staged dialog editing flows.
- Move into :mod:`foundry.features.rom_reload` or
  :mod:`foundry.features.online_updates` when the issue crosses the shell
  boundary into application features.
- Keep :doc:`../api/foundry_gui` open beside this page when you need generated
  module and class reference for the GUI code paths above.
