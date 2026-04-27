GUI and Editor Workflow
=======================

Start here for the editor shell, interactive views, and command-driven editing
workflows.

- :class:`~foundry.gui.FoundryMainWindow.FoundryMainWindow` is the application
  shell that coordinates ROM sessions, the active level or world surface, and
  the handoff into tool windows, dialogs, and command-driven edits.
- :mod:`foundry.gui.dialogs` contains the short-lived workflow branches that
  hang off the shell for recovery, parsing, settings, and focused editing
  tasks.
- :mod:`foundry.gui.level_settings` contains mixin-based editors that stage
  special enemy-item and ROM-table metadata before converting it back into
  undoable commands at dialog close time.
- :mod:`foundry.gui.commands` owns the undoable mutations that preserve editor
  intent as users move from gestures and dialog commits into replayable state
  changes.
- :class:`~foundry.gui.visualization.MainView.MainView` provides shared
  interaction behavior for level and world surfaces before those gestures are
  translated into commands.
- :class:`~foundry.gui.visualization.level.LevelView.LevelView` and
  :class:`~foundry.gui.visualization.world.WorldView.WorldView` turn gestures,
  selections, and drags into command construction plus repaint boundaries.
- :mod:`foundry.gui.windows` contains inspector and debugging windows that
  branch off the main workflow once a maintainer needs a denser read-only or
  investigative surface.
- :mod:`foundry.gui.widgets` contains reusable tool, status, size-bar, and
  table widgets that keep those larger shells and inspectors from duplicating
  shared interaction elements.
- :mod:`foundry.features.instaplay` stages the active level into a throwaway
  ROM flow so editor state can be exercised immediately in an emulator.
- :mod:`foundry.features.online_updates` keeps update checks, release-channel
  prompts, and application-shell follow-up work attached to the editor
  experience instead of scattering that workflow across startup code.
- :mod:`scribe.gui.main_window` mirrors that editor-shell role for the
  overworld tool, while :mod:`scribe.gui.world_overview`,
  :mod:`scribe.gui.tool_window`, and :mod:`scribe.gui.menus` break the same
  workflow into focused world interaction, inspector, and command-dispatch
  surfaces.
- :mod:`scribe.gui.edit_world_info` is the world-metadata staging dialog, and
  :mod:`scribe.gui.menus.edit_menu` owns the menu actions that hand off into
  that dialog and the shared undo stack.

Read this next:
:doc:`/subsystems/foundry_gui_architecture`,
:doc:`/subsystems/scribe_gui_architecture`
