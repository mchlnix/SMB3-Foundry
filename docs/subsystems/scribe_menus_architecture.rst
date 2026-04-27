Scribe Menus Architecture
=========================

This page covers the menu family rooted at :mod:`scribe.gui.menus`.

Problem and Context
-------------------

Scribe needs menu actions for undo or redo, bulk world edits, view persistence,
support links, and world metadata dialogs, but the menus should not become a
second application shell that owns its own world state. The menu package exists
to adapt user-facing menu actions onto the real editor collaborators that
already own the world model, settings, and undo history.

Goals
-----

- Provide menu-bar entry points for the most common Scribe workflows.
- Reuse existing editor services such as the shared undo stack, world view, and
  settings store instead of duplicating state.
- Keep menu actions synchronized with persisted settings and active editor
  state.
- Tailor shared Foundry help behavior to Scribe's overworld-focused scope.

Non-Goals
---------

- Own the main editor session; that remains in
  :class:`scribe.gui.main_window.ScribeMainWindow`.
- Implement the underlying world mutations directly when a collaborator already
  owns them.
- Replace dialogs or tool windows for complex editing tasks.

Current State
-------------

- :class:`scribe.gui.menus.edit_menu.EditMenu` adapts undo or redo, bulk-clear
  actions, and the world-info dialog onto the parent editor's shared undo stack
  and world view.
- :class:`scribe.gui.menus.view_menu.ViewMenu` is the persistence boundary for
  world-view overlay toggles and screenshot export. It seeds action state from
  saved settings and writes changes back through the same settings object.
- :class:`scribe.gui.menus.help_menu.HelpMenu` subclasses Foundry's help menu,
  removes level-editor-specific support actions, and swaps in Scribe's about
  dialog.

Data Flow
---------

1. :class:`scribe.gui.main_window.ScribeMainWindow` constructs the menu objects
   and attaches them to the menu bar.
2. Menu constructors resolve the parent editor's collaborators, chiefly the
   shared undo stack, active world view, and settings object.
3. Triggered actions either forward directly into those collaborators or launch
   dialogs such as :class:`scribe.gui.edit_world_info.EditWorldInfo`.
4. Settings-backed actions in :class:`scribe.gui.menus.view_menu.ViewMenu`
   write updated flags back to persistent settings, and the world view re-reads
   that state on redraw or next session startup.

Control Flow
------------

1. The main window creates the menu family during shell setup.
2. Qt routes menu activation through each menu's shared trigger dispatcher.
3. The dispatcher chooses the owning collaborator: undo stack, world view,
   settings store, screenshot export helper, or modal dialog.
4. Any resulting mutations or staging workflows continue outside the menu
   package, in the command layer, world view, or world-info dialog.

Architectural Decisions
-----------------------

Menus are adapters, not state owners
   Each menu looks up the parent editor's real collaborators on demand instead
   of maintaining separate world or settings state.

Persist view toggles through the settings store
   :class:`scribe.gui.menus.view_menu.ViewMenu` treats saved settings as the
   source of truth for overlay visibility, which keeps the first paint and
   later sessions aligned with previous user choices.

Reuse Foundry help behavior selectively
   :class:`scribe.gui.menus.help_menu.HelpMenu` inherits the broader support
   workflow and prunes the entries that only make sense for Foundry's level
   editor.

Route complex edits into dialogs or world-view helpers
   Bulk tile, sprite, and pointer clearing goes to the world view, while
   cross-world metadata and ordering edits go to
   :class:`scribe.gui.edit_world_info.EditWorldInfo`. The menus stay thin by
   not replicating those workflows inline.

Read This Next
--------------

- Read :doc:`scribe_gui_architecture` for the main window that hosts these
  menus.
- Read :doc:`scribe_commands_architecture` to follow edit-menu actions into the
  shared undo history.
- Read :class:`scribe.gui.menus.view_menu.ViewMenu` when the question is about
  settings-backed overlay visibility or screenshot export.
- Read :class:`scribe.gui.edit_world_info.EditWorldInfo` for the modal
  metadata and world-overview workflow launched from the edit menu.
