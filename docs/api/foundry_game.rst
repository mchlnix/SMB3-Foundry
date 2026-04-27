Foundry Game Modules
====================

These pages surface the core ROM-backed model modules that the editor, command
stack, and rendering layers all build on.

Start with the level and world abstractions when you need the main editing
objects. Follow the ROM file layer when you need persistence boundaries, and
move into object-definition and graphics-set modules when you are tracing how
raw SMB3 identifiers become richer editor-facing data.

This API surface is deliberately selective. It highlights the modules that own
long-lived game-model contracts rather than mirroring every package boundary,
so maintainers can move from high-level level or world state toward the
supporting ROM and rendering metadata without getting lost in implementation
detail.

Architecture Guides
-------------------

- :doc:`/subsystems/foundry_game_architecture` explains the shared problem
  space behind the ROM-backed model layer.
- :doc:`/subsystems/foundry_game_level_architecture` focuses on
  :mod:`foundry.game.level` workflows and persistence-sensitive state.
- :doc:`/subsystems/level_world_model` and
  :doc:`/subsystems/rom_data_persistence` provide the model and persistence
  routes that sit beside this API surface.

.. autosummary::
   :toctree: generated

   foundry.game.level.Level
   foundry.game.level.WorldMap
   foundry.game.File
   foundry.game.Data
   foundry.game.ObjectDefinitions
   foundry.game.ObjectSet
   foundry.game.gfx.GraphicsSet
   foundry.game.gfx.drawable.Block
