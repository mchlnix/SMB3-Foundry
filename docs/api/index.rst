API Navigation
==============

These pages surface important modules directly from the codebase. The goal is
not to mirror every package boundary, but to make the most important
relationships easy to follow from autodoc output.

For package-family context, goals, data flow, and architectural decisions, use
the architecture guides linked from each landing page and from
:doc:`/subsystems/index`.

.. toctree::
   :maxdepth: 1

   foundry_features
   foundry_game
   foundry_game_gfx
   foundry_game_level
   foundry_gui
   foundry_gui_commands
   foundry_gui_dialogs
   foundry_gui_windows
   foundry_gui_widgets
   smb3parse
   scribe_gui

Guide Pairings
--------------

Use these routes when you want the code reference and the maintainer guide open
side by side:

- Foundry GUI: :doc:`foundry_gui` with
  :doc:`/subsystems/foundry_gui_architecture`.
- Foundry game model: :doc:`foundry_game` with
  :doc:`/subsystems/foundry_game_architecture` and
  :doc:`/subsystems/level_world_model`.
- Foundry graphics: :doc:`foundry_game_gfx` with
  :doc:`/subsystems/foundry_game_gfx_architecture`,
  :doc:`/subsystems/graphics_rendering`, and
  :doc:`/subsystems/enemy_sprite_catalog`.
- Scribe GUI: :doc:`scribe_gui` with
  :doc:`/subsystems/scribe_gui_architecture`.
- SMB3 parsing: :doc:`smb3parse` with
  :doc:`/subsystems/smb3parse_parser_architecture`.
