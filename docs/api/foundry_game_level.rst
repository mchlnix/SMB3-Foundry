Foundry Level Model Modules
===========================

These pages surface ROM-backed level and world-model abstractions that feed the
editor and serializer layers.

Start with :class:`~foundry.game.level.Level` when you need the in-level
editing contract, object and enemy ownership, or the handoff into
serialization and replay-sensitive tools. Start with
:class:`~foundry.game.level.WorldMap` when you are following overworld layout,
special-level destinations, or world-specific rendering state.
:class:`~foundry.game.level.LevelRef` and :mod:`foundry.game.additional_data`
then fill in the lighter-weight references and editor-only metadata that orbit
those heavier model objects.

The useful path through this surface is usually model -> supporting metadata ->
serializer or renderer, not path-by-path traversal of the package tree. These
entries are ordered to make that path obvious.

Architecture Guides
-------------------

- :doc:`/subsystems/foundry_game_level_architecture` captures the goals,
  control flow, and long-lived constraints for the level-model family.
- :doc:`/subsystems/foundry_game_architecture` provides the wider game-model
  context around those level and world abstractions.
- :doc:`/subsystems/level_world_model` is the subsystem route map when you need
  parser, editor-model, and serializer boundaries together.

.. autosummary::
   :toctree: generated

   foundry.game.level.Level
   foundry.game.level.WorldMap
   foundry.game.level.LevelRef
   foundry.game.level.LevelLike
   foundry.game.additional_data
