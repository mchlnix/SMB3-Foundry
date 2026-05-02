Command, Undo, and Replay
=========================

Start here for undoable editor actions, serialized command payloads, and the
replay boundaries used by save, reload, and debugging tools.

- :mod:`foundry.gui.commands` owns the command types that preserve editor
  intent across undo, redo, replay, and ROM-write workflows.
- :mod:`foundry.gui.level_settings` is a major producer surface for those
  command types because its dialog mixins stage enemy, pipe, chest, and
  autoscroll edits before committing them as undoable changes.
- :mod:`scribe.gui.commands` applies the same command-and-undo model to SMB3
  Scribe's overworld editing workflow.
- :mod:`scribe.gui.edit_world_info` and :mod:`scribe.gui.world_overview` are
  the main producer surfaces for those Scribe commands, turning button
  presses, tile edits, and world metadata changes into undoable state
  transitions.
- :class:`~foundry.gui.visualization.level.LevelView.LevelView` and
  :class:`~foundry.gui.visualization.world.WorldView.WorldView` translate user
  gestures into command construction.
- :mod:`foundry.features.rom_reload` replays command history after ROM-backed
  state is refreshed.

Read this next:
:doc:`/subsystems/foundry_gui_architecture`,
:doc:`/subsystems/scribe_commands_architecture`
